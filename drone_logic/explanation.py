def explain_unified_conflicts(unified_conflicts):
    """
    Explain unified conflicts that combine spatial and temporal detection
    """
    return {
        "unified": unified_conflicts,
        "total": len(unified_conflicts),
        "summary": {
            "conflict_count": len(unified_conflicts),
            "affected_drones": len(set(c["drone"] for c in unified_conflicts)),
            "time_periods": list(set(c["time"] for c in unified_conflicts))
        }
    }