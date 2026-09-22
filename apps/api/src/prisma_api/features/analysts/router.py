from fastapi import APIRouter

from prisma_api.core.deps import DbSession
from prisma_api.features.analysts.mappers import analyst_to_schema
from prisma_api.features.analysts.schemas import AnalystSchema
from prisma_api.features.analysts.service import AnalystService

router = APIRouter()


@router.get("", response_model=list[AnalystSchema])
def list_analysts(db: DbSession) -> list[AnalystSchema]:
    service = AnalystService(db)
    return [analyst_to_schema(a) for a in service.list_analysts()]
