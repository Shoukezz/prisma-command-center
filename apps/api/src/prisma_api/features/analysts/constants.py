"""Analyst specialty and bias definitions."""

# Maps intel collection source to analyst specialty affinity.
SOURCE_SPECIALTY_AFFINITY = {
    "SATINT": "satellite_imagery",
    "SIGINT": "signals_intelligence",
    "HUMINT": "human_source",
    "CYBER": "cyber_threats",
}

BIAS_HAWKISH = "hawkish"
BIAS_SKEPTICAL = "skeptical"
BIAS_CYBER_FOCUS = "cyber_focus"
BIAS_DIPLOMATIC = "diplomatic"
BIAS_TECH_OPTIMIST = "tech_optimist"

ASSESSMENTS_PER_REPORT_MIN = 2
ASSESSMENTS_PER_REPORT_MAX = 3
