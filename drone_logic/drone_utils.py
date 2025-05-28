from datetime import datetime, timedelta

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
        # If all times are the same, just return one position
        unique_positions[times[0]] = waypoints[0]
        print(f"DEBUG - {drone['id']}: Hovering drone, single position at {times[0]}")
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
                if current_time not in unique_positions:  # Avoid overwriting existing positions
                    pos = interpolate_position(waypoints[i], waypoints[i + 1], t1, t2, current_time)
                    unique_positions[current_time] = pos

    # Add final position (only if not already added)
    final_time = times[-1]
    if final_time not in unique_positions:
        unique_positions[final_time] = waypoints[-1]

    # Convert back to sorted list of tuples
    sorted_times = sorted(unique_positions.keys(), key=lambda x: parse_time_str(x))
    positions = [(t, unique_positions[t]) for t in sorted_times]

    print(f"DEBUG - {drone['id']}: Generated {len(positions)} unique positions")
    for t, pos in positions:
        print(f"  {t}: [{pos[0]:.5f}, {pos[1]:.5f}]")

    return positions