from prisma_api.features.analysts.schemas import AnalystAssessmentSchema, AnalystSchema
from prisma_api.models import Analyst, AnalystAssessment


def analyst_to_schema(analyst: Analyst) -> AnalystSchema:
    return AnalystSchema(
        id=analyst.id,
        name=analyst.name,
        specialty=analyst.specialty,
        reliability=analyst.reliability,
        bias=analyst.bias,
    )


def assessment_to_schema(row: AnalystAssessment) -> AnalystAssessmentSchema:
    analyst = row.analyst
    return AnalystAssessmentSchema(
        id=row.id,
        analyst_id=row.analyst_id,
        analyst_name=analyst.name if analyst else "Невідомий",
        specialty=analyst.specialty if analyst else "",
        bias=analyst.bias if analyst else "",
        reliability=analyst.reliability if analyst else 0.0,
        assessment=row.assessment,
        assessed_confidence=row.assessed_confidence,
        timestamp=row.game_minutes,
    )
