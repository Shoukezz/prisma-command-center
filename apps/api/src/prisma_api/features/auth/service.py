from prisma_api.features.auth.repository import AuthRepository


class AuthService:
    """Authentication and session business logic."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository
