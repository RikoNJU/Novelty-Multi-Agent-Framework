"""查新点结果持久化（测试版）。

注意：当前实现只把查新点结果写入本地固定目录（``output/novelty_points/``），
属于测试版文件持久化，仅供开发验证。后续必须替换为数据库等生产存储
（如 PostgreSQL / Redis），届时仅需替换本模块的实现，调用方不变。
"""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import NoveltyPoint, PaperInput

# 固定输出目录（测试版；正式版应改为数据库写入）
DEFAULT_POINTS_DIR = Path("output/novelty_points")

# 持久化版本标记：用于区分测试版本地文件与后续生产存储
STORAGE_VERSION = "test-version-local-file"


def persist_novelty_points(
    paper: PaperInput,
    points: list[NoveltyPoint],
    *,
    output_dir: str | Path = DEFAULT_POINTS_DIR,
) -> Path:
    """把查新点写入固定目录（测试版持久化，后续替换为数据库）。"""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "storage": STORAGE_VERSION,
        "note": "测试版本地文件持久化，后续需替换为数据库等持久化存储",
        "novelty_points": [point.model_dump(mode="json") for point in points],
    }
    path = directory / f"{paper.paper_id}.points.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path
