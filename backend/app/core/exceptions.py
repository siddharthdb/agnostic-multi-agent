class DomainError(Exception):
    """Base class for errors the routers translate into HTTP responses."""


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} '{entity_id}' not found")


class ConflictError(DomainError):
    pass


class ValidationFailedError(DomainError):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__(f"validation failed with {len(errors)} error(s)")


class UnsupportedProtocolError(DomainError):
    def __init__(self, protocol: str):
        self.protocol = protocol
        super().__init__(f"no adapter registered for protocol '{protocol}'")
