from prisma_api.features.game_session.repository import GameSessionRepository


class GameSessionService:
    """Game session lifecycle."""

    def __init__(self, repository: GameSessionRepository) -> None:
        self._repository = repository
