"""Deterministic retrieval-coverage assessment for one NoveltyPoint.

系统只有在"必要来源确实被检索过、而且检索本身成功"的前提下，才有资格出具
基于"未检索到"的结论。这件事必须由确定性代码判定：必要来源来自配置，每次
检索执行的成功与失败来自工具观测，都不允许由模型表述或推断。

覆盖状态（``CoverageState``）：

- ``complete``：每个必要来源都执行过，且没有任何失败/降级执行；
- ``partial``：部分必要来源未执行，或存在失败/降级执行；
- ``failed``：必要来源执行过，但全部失败；
- ``not_attempted``：没有任何必要来源的执行记录；
- ``unconfigured``：配置里没有任何可判定的必要来源，覆盖契约缺失。

只有 ``complete`` 允许基于"未检索到"的否定性结论（``novel`` /
``partially_novel``）。其余状态一律降级为证据不足，避免把"检索没做好"或
"根本没连上库"写成"具有新颖性"。
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from pydantic import Field

from ..schemas import (
    NoveltyPointReview,
    NoveltyVerdict,
    ReviewStatus,
    SearchExecution,
    SearchExecutionStatus,
    StrictModel,
    SupplementRequest,
)


class CoverageState(StrEnum):
    """单个查新点的检索覆盖状态。"""

    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"
    UNCONFIGURED = "unconfigured"


class SourceState(StrEnum):
    """单个来源在同一查新点内的执行状态。"""

    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"
    NON_EVIDENTIARY = "non_evidentiary"


class SourceCoverage(StrictModel):
    """一个来源在该查新点内的执行统计。"""

    source_id: str = Field(min_length=1)
    required: bool
    attempts: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    degraded: int = Field(ge=0)
    empty: int = Field(ge=0)
    state: SourceState


class RetrievalCoverage(StrictModel):
    """一个查新点的检索覆盖事实，用于约束否定性结论。"""

    novelty_point_id: str = Field(min_length=1)
    state: CoverageState
    required_sources: list[str] = Field(default_factory=list)
    zero_hit_sources: list[str] = Field(default_factory=list)
    failed_sources: list[str] = Field(default_factory=list)
    degraded_sources: list[str] = Field(default_factory=list)
    not_attempted_sources: list[str] = Field(default_factory=list)
    sources: list[SourceCoverage] = Field(default_factory=list)
    reason: str = Field(min_length=1)

    @property
    def permits_absence_conclusion(self) -> bool:
        """只有完整覆盖才允许出具"未检索到某技术"的结论。"""

        return self.state is CoverageState.COMPLETE


@dataclass(frozen=True)
class CoverageDowngrade:
    """一次因覆盖不完整而被强制降级的裁定。"""

    novelty_point_id: str
    previous_verdict: NoveltyVerdict
    coverage_state: CoverageState
    reason: str


#: 基于"未检索到"的裁定。覆盖不完整时这些裁定不得成立。
ABSENCE_BASED_VERDICTS: frozenset[NoveltyVerdict] = frozenset(
    {NoveltyVerdict.NOVEL, NoveltyVerdict.PARTIALLY_NOVEL}
)


def _database_search_config(
    runtime_config: Mapping[str, object] | None,
) -> Mapping[str, object]:
    if not isinstance(runtime_config, Mapping):
        return {}
    researcher = runtime_config.get("researcher")
    if not isinstance(researcher, Mapping):
        return {}
    tools = researcher.get("tools")
    if not isinstance(tools, Mapping):
        return {}
    database = tools.get("database_search")
    return database if isinstance(database, Mapping) else {}


def _provider_flags(
    runtime_config: Mapping[str, object] | None,
) -> list[tuple[str, bool, bool]]:
    """返回 ``(source_id, enabled, testing_only)``，按 source_id 去重排序。"""

    providers = _database_search_config(runtime_config).get("providers")
    if not isinstance(providers, Mapping):
        return []
    flags: dict[str, tuple[bool, bool]] = {}
    for raw_source_id, raw_options in providers.items():
        source_id = str(raw_source_id).strip().lower()
        if not source_id:
            continue
        options = raw_options if isinstance(raw_options, Mapping) else {}
        flags[source_id] = (
            bool(options.get("enabled", True)),
            bool(options.get("testing_only", False)),
        )
    return [
        (source_id, enabled, testing_only)
        for source_id, (enabled, testing_only) in sorted(flags.items())
    ]


def required_retrieval_sources(
    runtime_config: Mapping[str, object] | None,
) -> tuple[str, ...]:
    """读取覆盖契约：启用且非 ``testing_only`` 的数据库来源。"""

    return tuple(
        source_id
        for source_id, enabled, testing_only in _provider_flags(runtime_config)
        if enabled and not testing_only
    )


def testing_only_retrieval_sources(
    runtime_config: Mapping[str, object] | None,
) -> tuple[str, ...]:
    """返回只用于测试、不能支撑证据结论的来源。"""

    return tuple(
        source_id
        for source_id, enabled, testing_only in _provider_flags(runtime_config)
        if enabled and testing_only
    )


def _source_state(counts: Mapping[str, int], *, required: bool) -> SourceState:
    attempts = counts["attempts"]
    if attempts == 0:
        return SourceState.NOT_ATTEMPTED
    if counts["failed"] or counts["degraded"]:
        return SourceState.DEGRADED if counts["succeeded"] else SourceState.FAILED
    return SourceState.OK if counts["succeeded"] else SourceState.FAILED


def assess_point_coverage(
    *,
    novelty_point_id: str,
    executions: Sequence[SearchExecution],
    required_sources: Sequence[str],
    testing_only_sources: Sequence[str] = (),
) -> RetrievalCoverage:
    """把一个查新点的全部检索执行事实聚合为覆盖状态。"""

    required = sorted(
        {str(item).strip().lower() for item in required_sources if str(item).strip()}
    )
    testing_only = {
        str(item).strip().lower()
        for item in testing_only_sources
        if str(item).strip()
    }

    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "attempts": 0,
            "succeeded": 0,
            "failed": 0,
            "degraded": 0,
            "empty": 0,
        }
    )
    for execution in executions:
        source_id = str(execution.source_id).strip().lower()
        if not source_id:
            continue
        bucket = counts[source_id]
        bucket["attempts"] += 1
        if execution.status is SearchExecutionStatus.SUCCEEDED:
            bucket["succeeded"] += 1
            if not execution.results:
                bucket["empty"] += 1
        elif execution.status is SearchExecutionStatus.FAILED:
            bucket["failed"] += 1
        else:
            # PARTIAL / REQUIRES_HUMAN：拿到了部分答案，但不构成完整覆盖。
            bucket["degraded"] += 1

    for source_id in required:
        counts[source_id]

    sources: list[SourceCoverage] = []
    for source_id in sorted(counts):
        bucket = counts[source_id]
        is_required = source_id in required
        if source_id in testing_only:
            state = SourceState.NON_EVIDENTIARY
        else:
            state = _source_state(bucket, required=is_required)
        sources.append(
            SourceCoverage(
                source_id=source_id,
                required=is_required,
                attempts=bucket["attempts"],
                succeeded=bucket["succeeded"],
                failed=bucket["failed"],
                degraded=bucket["degraded"],
                empty=bucket["empty"],
                state=state,
            )
        )

    required_states = {item.source_id: item.state for item in sources if item.required}
    failed_sources = sorted(
        source_id
        for source_id, state in required_states.items()
        if state is SourceState.FAILED
    )
    not_attempted_sources = sorted(
        source_id
        for source_id, state in required_states.items()
        if state is SourceState.NOT_ATTEMPTED
    )
    degraded_sources = sorted(
        source_id
        for source_id, state in required_states.items()
        if state is SourceState.DEGRADED
    )
    zero_hit_sources = sorted(
        item.source_id
        for item in sources
        if item.required and item.empty and not item.failed and not item.degraded
    )

    if not required:
        state = CoverageState.UNCONFIGURED
        reason = "配置中没有任何可判定的必要来源。"
    elif all(item is SourceState.NOT_ATTEMPTED for item in required_states.values()):
        state = CoverageState.NOT_ATTEMPTED
        reason = f"没有任何必要来源的执行记录（必要来源：{'、'.join(required)}）。"
    elif all(
        item in {SourceState.FAILED, SourceState.NOT_ATTEMPTED}
        for item in required_states.values()
    ):
        state = CoverageState.FAILED
        reason = (
            "必要来源的检索执行全部失败（必要来源："
            f"{'、'.join(required)}；失败：{'、'.join(failed_sources) or '无'}；"
            f"未执行：{'、'.join(not_attempted_sources) or '无'}）。"
        )
    elif all(item is SourceState.OK for item in required_states.values()):
        state = CoverageState.COMPLETE
        reason = (
            "必要来源全部成功执行（必要来源："
            f"{'、'.join(required)}；零命中来源："
            f"{'、'.join(zero_hit_sources) or '无'}）。"
        )
    else:
        state = CoverageState.PARTIAL
        reason = (
            "部分必要来源未成功执行（必要来源："
            f"{'、'.join(required)}；失败：{'、'.join(failed_sources) or '无'}；"
            f"降级：{'、'.join(degraded_sources) or '无'}；"
            f"未执行：{'、'.join(not_attempted_sources) or '无'}）。"
        )

    return RetrievalCoverage(
        novelty_point_id=novelty_point_id,
        state=state,
        required_sources=required,
        zero_hit_sources=zero_hit_sources,
        failed_sources=failed_sources,
        degraded_sources=degraded_sources,
        not_attempted_sources=not_attempted_sources,
        sources=sources,
        reason=reason,
    )


def assess_coverage(
    *,
    point_ids: Sequence[str],
    task_results: Sequence[object],
    required_sources: Sequence[str],
    testing_only_sources: Sequence[str] = (),
) -> list[RetrievalCoverage]:
    """按查新点聚合全部 ResearchTask 的检索执行事实。"""

    executions_by_point: dict[str, list[SearchExecution]] = defaultdict(list)
    for result in task_results:
        point_id = getattr(result, "novelty_point_id", None)
        if not isinstance(point_id, str) or not point_id:
            continue
        for execution in getattr(result, "retrieval_executions", ()) or ():
            if isinstance(execution, SearchExecution):
                executions_by_point[point_id].append(execution)
    return [
        assess_point_coverage(
            novelty_point_id=point_id,
            executions=executions_by_point.get(point_id, []),
            required_sources=required_sources,
            testing_only_sources=testing_only_sources,
        )
        for point_id in point_ids
    ]


_ZERO_CARD_CAUSE: dict[CoverageState, str] = {
    CoverageState.COMPLETE: "检索完整执行但零命中",
    CoverageState.PARTIAL: "检索覆盖不完整",
    CoverageState.FAILED: "检索执行失败",
    CoverageState.NOT_ATTEMPTED: "没有检索执行记录",
    CoverageState.UNCONFIGURED: "检索覆盖契约缺失",
}


def zero_card_reason(coverage: RetrievalCoverage) -> str:
    """把某个查新点的 0 卡原因表述为确定性句子。

    “为什么这个点没有证据”必须与覆盖状态一致，因此这句话由代码生成，不交给
    模型措辞：否则检索失败与检索成功但零命中会在产物里写成同一句话。
    """

    cause = _ZERO_CARD_CAUSE[coverage.state]
    if coverage.state is CoverageState.COMPLETE:
        return (
            f"{cause}；{coverage.reason}"
            "在本次检索范围内未见相同报道，但该结论受检索范围限制，需人工确认。"
        )
    return f"{cause}；{coverage.reason}该情形无法判定是否存在相关文献。"


def coverage_limitations(
    coverages: Sequence[RetrievalCoverage],
    *,
    zero_card_points: Sequence[str] = (),
) -> list[str]:
    """生成报告 limitations 的确定性条目。

    覆盖不完整的点无论有无卡片都要写入；完整覆盖但 0 卡的点只写“零命中”事实。
    完整覆盖且有卡片的点不写，避免报告被无意义的行淹没。
    """

    zero_cards = {str(item) for item in zero_card_points}
    lines: list[str] = []
    for coverage in coverages:
        if coverage.permits_absence_conclusion and (
            coverage.novelty_point_id not in zero_cards
        ):
            continue
        lines.append(
            f"{coverage.novelty_point_id}：{zero_card_reason(coverage)}"
        )
    return lines


def apply_coverage_policy(
    reviews: Sequence[NoveltyPointReview],
    coverages: Sequence[RetrievalCoverage],
    *,
    restricted_verdicts: frozenset[NoveltyVerdict] = ABSENCE_BASED_VERDICTS,
) -> tuple[list[NoveltyPointReview], list[CoverageDowngrade]]:
    """把覆盖不完整时的否定性裁定降级为证据不足。

    只改写裁定字段：``highly_relevant_works`` 是 Reviewer 基于已检索证据给出的
    事实，予以保留；``verdict`` / ``verdict_reason`` / ``confidence`` 属于被撤销
    的判断，全部清除。
    """

    coverage_by_point = {
        coverage.novelty_point_id: coverage for coverage in coverages
    }
    enforced: list[NoveltyPointReview] = []
    downgrades: list[CoverageDowngrade] = []
    for review in reviews:
        coverage = coverage_by_point.get(review.novelty_point_id)
        if (
            coverage is None
            or coverage.permits_absence_conclusion
            or review.status is not ReviewStatus.REVIEWED
            or review.verdict is None
            or review.verdict not in restricted_verdicts
        ):
            enforced.append(review)
            continue
        reason = (
            "检索覆盖不完整，不允许出具基于未检索到文献的裁定"
            f"（原裁定 {review.verdict.value}）。{coverage.reason}"
        )
        enforced.append(
            NoveltyPointReview(
                novelty_point_id=review.novelty_point_id,
                status=ReviewStatus.INSUFFICIENT_EVIDENCE,
                highly_relevant_works=list(review.highly_relevant_works),
                supplement_request=SupplementRequest(reason=reason),
            )
        )
        downgrades.append(
            CoverageDowngrade(
                novelty_point_id=review.novelty_point_id,
                previous_verdict=review.verdict,
                coverage_state=coverage.state,
                reason=reason,
            )
        )
    return enforced, downgrades
