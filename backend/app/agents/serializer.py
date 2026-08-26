from app.agents.manifest import AgentManifest
from app.agents.task import TaskResult


class AgentSerializer:
    @staticmethod
    def manifest_to_json(manifest: AgentManifest) -> str:
        return manifest.model_dump_json(indent=2)

    @staticmethod
    def task_result_to_json(result: TaskResult) -> str:
        return result.model_dump_json(indent=2)
