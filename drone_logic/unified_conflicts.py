from geopy.distance import geodesic
import math
from .drone_utils import get_positions_over_time

def check_unified_conflicts(primary, others, horizontal_threshold_m=50, vertical_threshold_m=25):
    """
    Unified conflict detection that checks 3D proximity at specific times
    Returns consolidated conflicts (one per actual conflict situation)
    """
    conflicts = []
    primary_positions = get_positions_over_time(primary)
    primary_altitude = primary.get("altitude", 100)  # Default altitude

    print(f"DEBUG - Primary drone positions: {len(primary_positions)}")

    for other in others:
        other_positions = get_positions_over_time(other)
        other_altitude = other.get("altitude", 100)  # Default altitude
        other_dict = {t: pos for t, pos in other_positions}

        print(f"DEBUG - {other['id']} positions: {len(other_positions)}")

        for t, primary_pos in primary_positions:
            if t in other_dict:
                other_pos = other_dict[t]
                
                # Calculate horizontal distance
                horizontal_dist = geodesic(primary_pos, other_pos).meters
                
                # Calculate vertical distance
                vertical_dist = abs(primary_altitude - other_altitude)
                
                # Check if within 3D conflict zone
                if horizontal_dist <= horizontal_threshold_m and vertical_dist <= vertical_threshold_m:
                    # Calculate 3D distance for reference
                    distance_3d = math.sqrt(horizontal_dist**2 + vertical_dist**2)
                    
                    conflicts.append({
                        "drone": other["id"],
                        "location": primary_pos,  # Use primary position as conflict location
                        "time": t,
                        "horizontal_distance_m": round(horizontal_dist, 2),
                        "vertical_distance_m": round(vertical_dist, 2),
                        "distance_3d_m": round(distance_3d, 2),
                        "primary_altitude": primary_altitude,
                        "other_altitude": other_altitude
                    })
                    
                    print(f"UNIFIED CONFLICT: Primary vs {other['id']} at {t}")
                    print(f"  Location: [{primary_pos[0]:.5f}, {primary_pos[1]:.5f}]")
                    print(f"  Horizontal: {horizontal_dist:.1f}m, Vertical: {vertical_dist:.1f}m, 3D: {distance_3d:.1f}m")
    
    print(f"Total unified conflicts found: {len(conflicts)}")
    return conflicts