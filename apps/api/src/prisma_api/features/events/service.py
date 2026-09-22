from prisma_api.features.events.repository import EventsRepository


class EventsService:
    """Event engine orchestration."""

    def __init__(self, repository: EventsRepository) -> None:
        self._repository = repository
