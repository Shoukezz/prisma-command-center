from prisma_api.features.operations.schemas import (
    AssetSchema,
    OperationResultSchema,
    OperationSchema,
)
from prisma_api.models import Asset, Operation


def asset_to_schema(asset: Asset) -> AssetSchema:
    return AssetSchema(
        id=asset.id,
        name=asset.name,
        asset_type=asset.asset_type,
        status=asset.status,
        supports_recon=asset.supports_recon,
        supports_strike=asset.supports_strike,
    )


def operation_to_schema(operation: Operation) -> OperationSchema:
    result_schema = None
    if operation.result is not None:
        result_schema = OperationResultSchema(
            success=operation.result.success,
            outcome_summary=operation.result.outcome_summary,
            confidence_at_planning=operation.result.confidence_at_planning,
            completed_at=operation.result.completed_at,
        )
    return OperationSchema(
        id=operation.id,
        operation_type=operation.operation_type,
        status=operation.status,
        region_name=operation.region_name,
        intel_confidence=operation.intel_confidence,
        started_at=operation.started_at,
        completes_at=operation.completes_at,
        duration_minutes=operation.duration_minutes,
        asset_id=operation.asset_id,
        asset_name=operation.asset.name if operation.asset else "",
        intel_report_id=operation.intel_report_id,
        result=result_schema,
    )
