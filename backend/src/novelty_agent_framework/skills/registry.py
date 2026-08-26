"""Filesystem-backed skill discovery with lazy body loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SkillRegistryError(ValueError):
    """Invalid skill package or lookup."""


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    path: Path

    def model_view(self) -> dict[str, str]:
        return {"name": self.name, "description": self.description}


class SkillRegistry:
    """Index metadata eagerly while retaining bodies on disk until requested."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self._skills: dict[str, SkillMetadata] = {}

    @classmethod
    def scan(cls, root: str | Path) -> "SkillRegistry":
        registry = cls(root)
        if not registry.root.exists():
            return registry
        if not registry.root.is_dir():
            raise SkillRegistryError(f"skill root is not a directory: {registry.root}")
        for path in sorted(registry.root.rglob("SKILL.md")):
            metadata, _ = _parse_skill(path)
            if metadata.name in registry._skills:
                previous = registry._skills[metadata.name]
                raise SkillRegistryError(
                    f"duplicate skill name {metadata.name!r}: "
                    f"{previous.path} and {path}"
                )
            registry._skills[metadata.name] = metadata
        return registry

    def list_metadata(self) -> tuple[SkillMetadata, ...]:
        return tuple(self._skills[name] for name in sorted(self._skills))

    def catalog(self) -> tuple[dict[str, str], ...]:
        return tuple(item.model_view() for item in self.list_metadata())

    def get(self, name: str) -> SkillMetadata:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise SkillRegistryError(f"unknown skill {name!r}") from exc

    def load(self, name: str) -> str:
        metadata = self.get(name)
        reparsed, body = _parse_skill(metadata.path)
        if reparsed.name != metadata.name:
            raise SkillRegistryError(f"skill metadata changed after scan: {name!r}")
        return body


def _parse_skill(path: Path) -> tuple[SkillMetadata, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SkillRegistryError(f"cannot read skill file: {path}") from exc
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillRegistryError(f"invalid frontmatter in {path}: missing opener")
    try:
        end = next(
            index for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as exc:
        raise SkillRegistryError(f"invalid frontmatter in {path}: missing closer") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            raise SkillRegistryError(f"invalid frontmatter line in {path}: {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key or not value or key in values:
            raise SkillRegistryError(f"invalid frontmatter field in {path}: {key!r}")
        values[key] = _unquote(value)

    name = values.get("name", "").strip()
    description = values.get("description", "").strip()
    if not name:
        raise SkillRegistryError(f"skill is missing name: {path}")
    if not description:
        raise SkillRegistryError(f"skill is missing description: {path}")
    body = "\n".join(lines[end + 1 :]).strip()
    return SkillMetadata(name=name, description=description, path=path), body


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
