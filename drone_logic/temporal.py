from geopy.distance import geodesic
from .drone_utils import get_positions_over_time

def check_temporal_conflicts(primary, others, threshold_meters=50):
    """
    Legacy temporal conflict detection - kept for backwards compatibility
    Consider using check_unified_conflicts() for better 3D conflict detection
    """
    conflicts = []
    primary_positions = get_positions_over_time(primary)

    for other in others:
        other_positions = get_positions_over_time(other)
        other_dict = {t: pos for t, pos in other_positions}

        for t, pos1 in primary_positions:
            if t in other_dict:
                dist = geodesic(pos1, other_dict[t]).meters
                if dist <= threshold_meters:
                    conflicts.append({
                        "drone": other["id"],
                        "location": pos1,
                        "time": t,
                        "distance_m": round(dist, 2)
                    })
                    print(f"CONFLICT: Primary vs {other['id']} at {t} - {dist:.1f}m")
    
    print(f"Total conflicts found: {len(conflicts)}")
    return conflicts