"""Deployment serializer — JSON serialization helpers."""

import json
from dataclasses import asdict, is_dataclass
from typing import Any


class DeploymentSerializer:
    @staticmethod
    def to_dict(obj: Any) -> dict[str, Any]:
        if is_dataclass(obj):
            return asdict(obj)
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return dict(obj)

    @staticmethod
    def to_json(obj: Any) -> str:
        return json.dumps(DeploymentSerializer.to_dict(obj), default=str)
