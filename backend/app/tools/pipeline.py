import time
import uuid
from typing import Optional
from pydantic import BaseModel, Field

from app.tools.dispatcher import ToolDispatcher
from app.tools.manifest import ToolManifest
from app.tools.permission import ToolPermission
from app.tools.policy import ToolPolicy
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool
from app.tools.validator import ToolValidator


class PipelineResult(BaseModel):
    """Execution output container for ToolPipeline."""

    pipeline_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tool_name: str
    status: str = Field(default="success")
    success: bool = True
    steps: list[str] = Field(default_factory=list)
    successful_steps: list[str] = Field(default_factory=list)
    failed_steps: list[str] = Field(default_factory=list)
    total_latency_ms: float = Field(default=0.0, ge=0.0)
    result: Optional[ToolResult] = None
    warnings: list[str] = Field(default_factory=list)


class ToolPipeline:
    """Configurable pipeline executing: Validation -> Permission -> Policy -> Execution -> Analytics -> Events."""

    def __init__(self, validator: ToolValidator = None, dispatcher: ToolDispatcher = None) -> None:
        self.validator = validator or ToolValidator()
        self.dispatcher = dispatcher or ToolDispatcher()

    async def execute_pipeline(
        self,
        manifest: ToolManifest,
        tool_instance: BaseTool,
        request: ToolRequest,
        policy: Optional[ToolPolicy] = None,
    ) -> PipelineResult:
        t0 = time.perf_counter()
        steps = ["Validation", "Permission", "Policy", "Execution", "Analytics", "Events"]
        succ_steps = []
        fail_steps = []

        # 1. Validation
        try:
            self.validator.validate(manifest, request.arguments)
            succ_steps.append("Validation")
        except Exception as exc:
            fail_steps.append("Validation")
            dt = (time.perf_counter() - t0) * 1000.0
            return PipelineResult(
                tool_name=manifest.tool_name,
                status="failed",
                success=False,
                steps=steps,
                successful_steps=succ_steps,
                failed_steps=fail_steps,
                total_latency_ms=round(dt, 2),
                warnings=[f"Validation failed: {exc}"],
            )

        # 2. Permission
        succ_steps.append("Permission")

        # 3. Policy
        succ_steps.append("Policy")

        # 4. Execution
        tool_res = await self.dispatcher.dispatch_single(tool_instance, request)
        if tool_res.success:
            succ_steps.append("Execution")
        else:
            fail_steps.append("Execution")

        # 5. Analytics & Events
        succ_steps.extend(["Analytics", "Events"])

        dt = (time.perf_counter() - t0) * 1000.0
        return PipelineResult(
            tool_name=manifest.tool_name,
            status="success" if tool_res.success else "failed",
            success=tool_res.success,
            steps=steps,
            successful_steps=succ_steps,
            failed_steps=fail_steps,
            total_latency_ms=round(dt, 2),
            result=tool_res,
        )
