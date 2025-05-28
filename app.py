import streamlit as st
from drone_logic.unified_conflicts import check_unified_conflicts
from drone_logic.explanation import explain_unified_conflicts
from map_visual.folium_plot import plot_flights_on_map
import json
from datetime import datetime, timedelta

st.set_page_config(layout="wide")  # Full-screen layout

# Sidebar input UI
with st.sidebar.expander("📋 Input & Conflict Detection", expanded=True):
    st.title("Drone Deconfliction")
    
    primary_waypoints = st.text_area("Primary Drone Waypoints (lat, lon)", 
        value="[[18.5204, 73.8567], [18.5304, 73.8667], [18.5404, 73.8767]]")

    primary_altitude = st.number_input("Primary Drone Altitude (meters)", value=100, min_value=50, max_value=500)
    
    start_time_str = st.text_input("Mission Start Time (HH:MM)", value="14:00")
    end_time_str = st.text_input("Mission End Time (HH:MM)", value="14:30")

    # Conflict detection parameters
    st.subheader("Conflict Detection Settings")
    horizontal_threshold = st.slider("Horizontal Threshold (meters)", 20, 100, 50)
    vertical_threshold = st.slider("Vertical Threshold (meters)", 10, 50, 25)

    check = st.button("Check for Conflicts")

# Load simulated drones
with open("data/sample_flights.json") as f:
    simulated_drones = json.load(f)

# Output placeholders
conflict_result = None
html_map = None

try:
    t_start = datetime.strptime(start_time_str, "%H:%M")
    t_end = datetime.strptime(end_time_str, "%H:%M")

    if t_end <= t_start:
        st.sidebar.error("❗ End time must be after start time.")
    else:
        waypoints = eval(primary_waypoints)
        segment_count = len(waypoints) - 1
        total_minutes = int((t_end - t_start).total_seconds() // 60)
        segment_time = total_minutes // segment_count

        times = [(t_start + timedelta(minutes=i * segment_time)).strftime("%H:%M") for i in range(len(waypoints))]

        primary = {
            "id": "primary",
            "waypoints": waypoints,
            "times": times,
            "altitude": primary_altitude
        }

        if check:
            # Use unified conflict detection
            unified_conflicts = check_unified_conflicts(
                primary, 
                simulated_drones, 
                horizontal_threshold_m=horizontal_threshold,
                vertical_threshold_m=vertical_threshold
            )
            
            explanation = explain_unified_conflicts(unified_conflicts)

            with st.sidebar.expander("🛑 Conflict Check Result", expanded=True):
                if explanation["total"] > 0:
                    st.markdown("### ⚠️ Conflicts Detected")
                    st.markdown(f"**Total Conflicts:** {explanation['total']}")
                    
                    # Show conflict summary
                    for conflict in unified_conflicts:
                        st.markdown(f"**{conflict['drone']}** at {conflict['time']}")
                        st.markdown(f"  • 3D Distance: {conflict['distance_3d_m']}m")
                        st.markdown(f"  • Location: [{conflict['location'][0]:.5f}, {conflict['location'][1]:.5f}]")
                else:
                    st.markdown("### ✅ No Conflicts Detected")

            # Create explanation object in expected format for map plotting
            explanation_for_map = {
                "unified": unified_conflicts,
                "total": len(unified_conflicts)
            }

            html_map = plot_flights_on_map(primary, simulated_drones, explanation_for_map).get_root().render()

except ValueError:
    st.sidebar.error("Invalid time format. Please use HH:MM.")
except Exception as e:
    st.sidebar.error(f"Error: {str(e)}")

# Map output on the right side full-screen
if html_map:
    st.components.v1.html(html_map, height=800)