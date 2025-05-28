from geopy.distance import geodesic
from datetime import datetime, timedelta
import math

def parse_time_str(t_str):
    return datetime.strptime(t_str, "%H:%M")

def interpolate_position(wp1, wp2, t1, t2, t):
    dt1, dt2, dt = parse_time_str(t1), parse_time_str(t2), parse_time_str(t)
    ratio = (dt - dt1).total_seconds() / (dt2 - dt1).total_seconds()
    lat = wp1[0] + ratio * (wp2[0] - wp1[0])
    lon = wp1[1] + ratio * (wp2[1] - wp1[1])
    return [lat, lon]

def get_positions_over_time(drone):
    times = drone["times"]
    waypoints = drone["waypoints"]
    
    # Use a dictionary to ensure unique timestamps
    unique_positions = {}

    # Handle edge case where all times are the same (hovering drone)
    if len(set(times)) == 1:
        unique_positions[times[0]] = waypoints[0]
        return [(times[0], waypoints[0])]

    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        
        # Skip if times are the same (duplicate timestamps)
        if t1 == t2:
            unique_positions[t1] = waypoints[i]
            continue
            
        dt1, dt2 = parse_time_str(t1), parse_time_str(t2)
        interval = int((dt2 - dt1).total_seconds() // 60)

        # Add start position (only if not already added)
        if t1 not in unique_positions:
            unique_positions[t1] = waypoints[i]

        # Add interpolated positions for each minute (skip if interval <= 1)
        if interval > 1:
            for m in range(1, interval):
                current_time = (dt1 + timedelta(minutes=m)).strftime("%H:%M")
                if current_time not in unique_positions:
                    pos = interpolate_position(waypoints[i], waypoints[i + 1], t1, t2, current_time)
                    unique_positions[current_time] = pos

    # Add final position (only if not already added)
    final_time = times[-1]
    if final_time not in unique_positions:
        unique_positions[final_time] = waypoints[-1]

    # Convert back to sorted list of tuples
    sorted_times = sorted(unique_positions.keys(), key=lambda x: parse_time_str(x))
    positions = [(t, unique_positions[t]) for t in sorted_times]

    return positions

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