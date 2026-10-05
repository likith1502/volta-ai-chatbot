"""Phase 7.8 — Enterprise Deployment Package.

Entry point and public surface for backend.app.deployment.
"""

from app.deployment.manager import DeploymentManager
from app.deployment.deployment import Deployment, DeploymentStatus
from app.deployment.lifecycle import DeploymentLifecycleState, DeploymentLifecycleManager
from app.deployment.release import ReleaseManager, ReleaseManifest
from app.deployment.strategy import DeploymentStrategy, BlueGreenDeployment, RollingDeployment, CanaryDeployment, RecreateDeployment
from app.deployment.rollback import RollbackManager, RollbackPlan
from app.deployment.scaling import AutoScalingPolicy, HorizontalScaling, VerticalScaling, ResourceLimits, ReplicaPolicy
from app.deployment.environment import Environment, EnvironmentManager
from app.deployment.validator import DeploymentValidator
from app.deployment.health import DeploymentHealthManager, DeploymentHealthReport, DeploymentHealthLevel
from app.deployment.backup import BackupManager, BackupPlan
from app.deployment.recovery import RecoveryManager, RecoveryPlan

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
