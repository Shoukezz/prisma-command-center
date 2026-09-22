from prisma_api.models.operations import OPERATION_RECON, OPERATION_STRIKE

OPERATION_TYPES = (OPERATION_RECON, OPERATION_STRIKE)

DURATION_MINUTES = {
    OPERATION_RECON: 45,
    OPERATION_STRIKE: 90,
}

# Base success modifier by operation type (before confidence).
TYPE_SUCCESS_MODIFIER = {
    OPERATION_RECON: 0.92,
    OPERATION_STRIKE: 0.72,
}

# Weight of player-visible confidence vs hidden intel accuracy.
CONFIDENCE_WEIGHT = 0.65
ACCURACY_WEIGHT = 0.35
