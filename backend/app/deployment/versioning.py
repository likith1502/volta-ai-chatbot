"""Deployment versioning utilities."""

import re
from dataclasses import dataclass


@dataclass
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version: str) -> "SemVer":
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if not m:
            raise ValueError(f"Invalid semver: {version}")
        return cls(major=int(m.group(1)), minor=int(m.group(2)), patch=int(m.group(3)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "SemVer") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def is_compatible_with(self, other: "SemVer") -> bool:
        """True if same major version."""
        return self.major == other.major

    def next_patch(self) -> "SemVer":
        return SemVer(self.major, self.minor, self.patch + 1)

    def next_minor(self) -> "SemVer":
        return SemVer(self.major, self.minor + 1, 0)

    def next_major(self) -> "SemVer":
        return SemVer(self.major + 1, 0, 0)
