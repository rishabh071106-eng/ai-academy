"""Configuration, profile loading, and company blocklist matching."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _normalize(name: str) -> str:
    """Lowercase and strip everything but letters/digits so that
    'J.P. Morgan', 'JP Morgan' and 'jpmorgan' all compare equal."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


@dataclass
class Blocklist:
    names: list[str]
    _normalized: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self._normalized = [_normalize(n) for n in self.names if n.strip()]

    def matches(self, company: str | None) -> bool:
        if not company:
            return False
        norm = _normalize(company)
        return any(b in norm or norm in b for b in self._normalized if b)


@dataclass
class Config:
    raw: dict
    profile: dict
    resume_master: str
    blocklist: Blocklist

    @property
    def model(self) -> str:
        return self.raw.get("model", "claude-opus-4-8")

    @property
    def search(self) -> dict:
        return self.raw.get("search", {})

    @property
    def companies(self) -> dict:
        return self.raw.get("companies", {}) or {}

    @property
    def policy(self) -> dict:
        return self.raw.get("policy", {})

    @property
    def title_pattern(self) -> re.Pattern:
        return re.compile(self.search.get("title_pattern", r"(?i)director|vp|head"))

    def path(self, key: str, default: str) -> Path:
        return ROOT / self.raw.get("paths", {}).get(key, default)


def load_config(config_path: Path | None = None) -> Config:
    cfg_file = config_path or ROOT / "config.yaml"
    raw = yaml.safe_load(cfg_file.read_text())
    profile = yaml.safe_load((ROOT / "profile" / "profile.yaml").read_text())
    resume_master = (ROOT / "profile" / "resume_master.md").read_text()
    return Config(
        raw=raw,
        profile=profile,
        resume_master=resume_master,
        blocklist=Blocklist(raw.get("blocklist", [])),
    )
