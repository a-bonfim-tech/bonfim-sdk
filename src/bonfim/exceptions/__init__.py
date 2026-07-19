"""Safe, classified SDK exceptions."""


class BonfimError(Exception):
    """Base class for expected SDK errors."""


class ValidationError(BonfimError):
    """A declared contract is invalid."""


class RegistrationError(BonfimError):
    """A component cannot be registered safely."""


class DiscoveryError(BonfimError):
    """An allowlisted plugin entry point cannot be loaded."""


class ExecutionError(BonfimError):
    """A component execution failed in an expected way."""


class GovernanceError(BonfimError):
    """A governance or authority boundary was violated."""


class RollbackError(BonfimError):
    """One or more explicit rollback operations failed."""


__all__ = [
    "BonfimError",
    "DiscoveryError",
    "ExecutionError",
    "GovernanceError",
    "RegistrationError",
    "RollbackError",
    "ValidationError",
]
