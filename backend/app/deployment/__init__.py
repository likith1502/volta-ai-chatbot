"""Phase 7.8 — Enterprise Deployment Package.

Entry point and public surface for backend.app.deployment.
"""

from app.deployment.backup import BackupManager, BackupPlan
from app.deployment.deployment import Deployment, DeploymentStatus
from app.deployment.environment import Environment, EnvironmentManager
from app.deployment.health import (
    DeploymentHealthLevel,
    DeploymentHealthManager,
    DeploymentHealthReport,
)
from app.deployment.lifecycle import (
    DeploymentLifecycleManager,
    DeploymentLifecycleState,
)
from app.deployment.manager import DeploymentManager
from app.deployment.recovery import RecoveryManager, RecoveryPlan
from app.deployment.release import ReleaseManager, ReleaseManifest
from app.deployment.rollback import RollbackManager, RollbackPlan
from app.deployment.scaling import (
    AutoScalingPolicy,
    HorizontalScaling,
    ReplicaPolicy,
    ResourceLimits,
    VerticalScaling,
)
from app.deployment.strategy import (
    BlueGreenDeployment,
    CanaryDeployment,
    DeploymentStrategy,
    RecreateDeployment,
    RollingDeployment,
)
from app.deployment.validator import DeploymentValidator

__all__ = [
    "DeploymentManager",
    "Deployment",
    "DeploymentStatus",
    "DeploymentLifecycleState",
    "DeploymentLifecycleManager",
    "ReleaseManager",
    "ReleaseManifest",
    "DeploymentStrategy",
    "BlueGreenDeployment",
    "RollingDeployment",
    "CanaryDeployment",
    "RecreateDeployment",
    "RollbackManager",
    "RollbackPlan",
    "AutoScalingPolicy",
    "HorizontalScaling",
    "VerticalScaling",
    "ResourceLimits",
    "ReplicaPolicy",
    "Environment",
    "EnvironmentManager",
    "DeploymentValidator",
    "DeploymentHealthManager",
    "DeploymentHealthReport",
    "DeploymentHealthLevel",
    "BackupManager",
    "BackupPlan",
    "RecoveryManager",
    "RecoveryPlan",
]
