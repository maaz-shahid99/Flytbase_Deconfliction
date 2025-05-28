import folium
from folium.plugins import TimestampedGeoJson
from drone_logic.drone_utils import get_positions_over_time

def plot_flights_on_map(primary, others, conflicts):
    fmap = folium.Map(location=primary['waypoints'][0], zoom_start=14)

    all_drones = [primary] + others
    features = []
    
    # Build a dict of {drone_id: set(conflict_time)} for termination logic
    conflict_stops = {}
    for c in conflicts.get("temporal", []):
        conflict_stops.setdefault(c["drone"], set()).add(c["time"])

    # Get list of drones that have conflicts with primary drone
    conflicting_drones = set()
    for conflict in conflicts.get("unified", []):
        conflicting_drones.add(conflict["drone"])

    # Debug: Print positions to check for duplicates
    print("DEBUG - Positions generated:")
    for drone in all_drones:
        positions = get_positions_over_time(drone)
        print(f"{drone['id']}: {len(positions)} positions")
        for timestamp, pos in positions:
            print(f"  {timestamp}: {pos}")
    
    for drone in all_drones:
        positions = get_positions_over_time(drone)
        altitude = drone.get("altitude", 100)
        
        print(f"{drone['id']}: Processing {len(positions)} positions")

        # Track processed time-position combinations to avoid duplicates
        processed_features = set()

        for timestamp, pos in positions:
            # Create a unique key for this time-position-drone combination
            feature_key = (drone['id'], timestamp, tuple(pos))
            
            if feature_key in processed_features:
                print(f"Skipping duplicate feature for {drone['id']} at {timestamp}")
                continue
            
            processed_features.add(feature_key)

            # Check if drone should stop due to conflicts
            stop_times = conflict_stops.get(drone["id"], set())
            if stop_times and timestamp > min(stop_times):
                continue

            # Determine marker color based on drone type and conflict status
            if drone['id'] == "primary":
                icon_color = "blue"
            elif drone['id'] in conflicting_drones:
                icon_color = "red"  # Mark conflicting drones in red
            else:
                icon_color = "green"

            popup_text = f"Drone: {drone['id']}<br>Time: {timestamp}<br>Lat: {pos[0]:.5f}<br>Lon: {pos[1]:.5f}<br>Altitude: {altitude} m"
            
            # Add conflict status to popup for conflicting drones
            if drone['id'] in conflicting_drones:
                popup_text += "<br><b style='color:red;'>⚠️ CONFLICT DRONE</b>"
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [pos[1], pos[0]]  # Folium uses [lon, lat]
                },
                "properties": {
                    "time": f"2024-01-01T{timestamp}:00",
                    "popup": popup_text,
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": icon_color,
                        "color": icon_color,
                        "fillOpacity": 0.8,
                        "weight": 2,
                        "radius": 6
                    }
                }
            })

        # Add flight path lines with different colors for conflicting drones
        if drone['id'] == "primary":
            # Primary drone gets a thicker blue line  
            folium.PolyLine(
                drone['waypoints'], 
                color="blue", 
                weight=4, 
                opacity=0.8,
                popup=f"Primary Drone Path"
            ).add_to(fmap)
        elif drone['id'] in conflicting_drones:
            # Conflicting drones get red lines
            folium.PolyLine(
                drone['waypoints'], 
                color="red", 
                weight=3, 
                opacity=0.7,
                popup=f"{drone['id']} Path (CONFLICT DRONE)"
            ).add_to(fmap)
        else:
            # Other drones get thinner gray lines
            folium.PolyLine(
                drone['waypoints'], 
                color="black", 
                weight=2, 
                opacity=0.6,
                popup=f"{drone['id']} Path"
            ).add_to(fmap)

    # Add the timestamped animation
    TimestampedGeoJson({
        "type": "FeatureCollection",
        "features": features
    }, 
    period="PT1M",  # 1 minute intervals
    duration="PT1M", # Each point visible for 1 minute
    add_last_point=True, 
    auto_play=False,  # Don't auto-play to avoid confusion
    loop=False
    ).add_to(fmap)

    # Add unified conflict markers (orange markers with warning icon for better visibility)
    for conflict in conflicts.get("unified", []):
        lat, lon = conflict["location"]
        
        # Create detailed popup with 3D conflict information
        popup_html = f"""
        <div style="width: 250px;">
            <h4>🚨 DRONE CONFLICT</h4>
            <b>Time:</b> {conflict['time']}<br>
            <b>Drones:</b> Primary & {conflict['drone']}<br>
            <b>Location:</b> [{lat:.5f}, {lon:.5f}]<br>
            <hr>
            <b>3D Distance:</b> {conflict['distance_3d_m']}m<br>
            <b>Horizontal:</b> {conflict['horizontal_distance_m']}m<br>
            <b>Vertical:</b> {conflict['vertical_distance_m']}m<br>
            <hr>
            <b>Altitudes:</b><br>
            • Primary: {conflict['primary_altitude']}m<br>
            • {conflict['drone']}: {conflict['other_altitude']}m
        </div>
        """
        
        # Use a more prominent marker that will show above other markers
        folium.Marker(
            location=(lat, lon),
            icon=folium.Icon(color="red", icon="exclamation-sign", prefix="fa"),
            popup=folium.Popup(popup_html, max_width=300),
            z_index_offset=1000  # Higher z-index to appear on top
        ).add_to(fmap)
        
        # Add a semi-transparent circle around conflict point for better visibility
        folium.CircleMarker(
            location=(lat, lon),
            radius=15,
            color="red",
            weight=3,
            opacity=0.8,
            fillColor="yellow",
            fillOpacity=0.3,
            z_index_offset=999
        ).add_to(fmap)

    # Add only start and end waypoint markers for reference (not all waypoints)
    folium.Marker(
        location=primary['waypoints'][0],
        icon=folium.Icon(color="darkblue", icon="play"),
        popup=f"Primary START<br>Lat: {primary['waypoints'][0][0]:.5f}<br>Lon: {primary['waypoints'][0][1]:.5f}"
    ).add_to(fmap)
    
    folium.Marker(
        location=primary['waypoints'][-1],
        icon=folium.Icon(color="darkblue", icon="stop"),
        popup=f"Primary END<br>Lat: {primary['waypoints'][-1][0]:.5f}<br>Lon: {primary['waypoints'][-1][1]:.5f}"
    ).add_to(fmap)

    # Enhanced legend with detailed conflict information
    conflicting_drone_names = ", ".join(sorted(conflicting_drones)) if conflicting_drones else "None"
    
    # Build detailed conflict list for legend
    conflict_details = ""
    if conflicts.get("unified"):
        conflict_details = "<p><strong>Active Conflicts:</strong></p>"
        for conflict in conflicts.get("unified", []):
            conflict_details += f"""
            <div style="font-size:10px; margin:2px 0; padding:2px; background:#ffeeee; border-left:3px solid red;">
                <strong>{conflict['drone']}</strong> at {conflict['time']}<br>
                📍 3D: {conflict['distance_3d_m']}m
            </div>
            """
    else:
        conflict_details = "<p style='color:green;'><strong>✅ No Active Conflicts</strong></p>"
    
    # Dynamic height based on number of conflicts
    legend_height = max(200, 180 + len(conflicts.get("unified", [])) * 35)
    
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 250px; height: {legend_height}px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                overflow-y: auto;">
    <p><strong style="font-size:14px;">🛸 Drone Conflict Map</strong></p>
    <hr style="margin: 5px 0;">
    <p><i class="fa fa-circle" style="color:blue"></i> Primary Drone</p>
    <p><i class="fa fa-circle" style="color:green"></i> Safe Drones</p>
    <p><i class="fa fa-circle" style="color:red"></i> <strong>Conflict Drones</strong></p>
    <p><i class="fa fa-warning" style="color:orange"></i> Conflict Locations</p>
    <hr style="margin: 5px 0;">
    {conflict_details}
    </div>
    '''
    fmap.get_root().html.add_child(folium.Element(legend_html))

    return fmap