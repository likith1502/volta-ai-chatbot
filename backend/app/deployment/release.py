"""Release Manager — semantic versioning, release manifests, compatibility validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class ReleaseManifest:
    """Full manifest for a platform release."""
    version: str
    release_name: str
    platform_version: str = "7.8.0"
    runtime_layers: list[str] = field(default_factory=lambda: [
        "v7.0-LLM-Runtime", "v7.1-Prompt", "v7.2-Memory", "v7.3-Tools",
        "v7.4-Graph", "v7.5-Agents", "v7.6-RAG", "v7.7-Integrations",
        "v7.8-Deployment",
    ])
    migration_scripts: list[str] = field(default_factory=list)
    rollback_version: Optional[str] = None
    compatible_with: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    release_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackMetadata:
    """Metadata for rollback targeting."""
    from_version: str
    to_version: str
    snapshot_id: str
    can_rollback: bool = True
    estimated_duration_seconds: int = 30


class ReleaseManager:
    """Manages semantic versioning, release manifests, and compatibility validation."""

    _SEM_VER_RE = re.compile(
        r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$"
    )

    def __init__(self) -> None:
        self._releases: dict[str, ReleaseManifest] = {}
        self._current_version: Optional[str] = None
        self._history: list[str] = []

    def register_release(self, manifest: ReleaseManifest) -> None:
        """Register a release manifest."""
        if not self.is_valid_semver(manifest.version):
            raise ValueError(f"Invalid semantic version: {manifest.version}")
        self._releases[manifest.version] = manifest
        if self._current_version is None:
            self._current_version = manifest.version
        self._history.append(manifest.version)

    def promote(self, version: str) -> bool:
        """Promote a version to the current release."""
        if version not in self._releases:
            return False
        self._current_version = version
        return True

    def get_manifest(self, version: str) -> Optional[ReleaseManifest]:
        return self._releases.get(version)

    def list_releases(self) -> list[ReleaseManifest]:
        return list(self._releases.values())

    @property
    def current_version(self) -> Optional[str]:
        return self._current_version

    @property
    def release_history(self) -> list[str]:
        return list(self._history)

    def is_valid_semver(self, version: str) -> bool:
        return bool(self._SEM_VER_RE.match(version))

    def validate_compatibility(self, from_version: str, to_version: str) -> dict[str, Any]:
        """Validates compatibility between two releases. Returns compatibility report."""
        from_m = self._releases.get(from_version)
        to_m = self._releases.get(to_version)
        breaking = to_m.breaking_changes if to_m else []
        return {
            "from_version": from_version,
            "to_version": to_version,
            "is_compatible": len(breaking) == 0,
            "breaking_changes": breaking,
            "migration_scripts": to_m.migration_scripts if to_m else [],
        }

    def build_rollback_metadata(self, from_version: str, to_version: str) -> RollbackMetadata:
        return RollbackMetadata(
            from_version=from_version,
            to_version=to_version,
            snapshot_id=f"snap_{to_version.replace('.', '_')}",
            can_rollback=to_version in self._releases,
        )
