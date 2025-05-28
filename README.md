# 🛸 Drone Deconfliction Simulator

An interactive simulator for visualizing and detecting spatio-temporal conflicts between autonomous drones based on flight paths, times, and altitudes.

## 🚀 Features

- Upload or define a **primary drone mission**
- Load pre-defined **simulated drone missions**
- Detect **3D conflicts** using unified horizontal & vertical thresholds
- Visualize **interpolated drone paths** with timestamps
- Interactive **Folium map** showing:
  - Conflict points with popup info
  - Animated flight paths
  - Real-time conflict markers and dynamic legend
- Easy-to-use **Streamlit web interface**

## 📁 Project Structure

├── app.py # Streamlit app entry point
├── data/
│ └── sample_flights.json # Predefined drone missions
├── drone_logic/
│ ├── drone_utils.py # Interpolation & position utilities
│ ├── temporal.py # (Legacy) 2D conflict detection
│ ├── unified_conflicts.py # 3D unified conflict detection
│ └── explanation.py # Conflict summarization
├── map_visual/
│ └── folium_plot.py # Map rendering and animations
├── utils.py # Extra utilities (e.g., distance)
├── requirements.txt # Python dependencies
└── README.md # Project overview


## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/drone-deconfliction-simulator.git
cd drone-deconfliction-simulator

```
### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```
### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### USAGE

```bash
streamlit run app.py
```

Navigate to http://localhost:8501

Input the primary drone's waypoints, times, and altitude

Adjust conflict detection thresholds

Click Check for Conflicts to view results and map

## 📊 Conflict Detection Logic
Spatial Interpolation: Positions generated per minute

Temporal Matching: Conflicts checked at matching timestamps

3D Detection:

Horizontal threshold (e.g., 50 meters)

Vertical threshold (e.g., 25 meters)

Combined into 3D distance calculation

## 📌 Technologies Used
Streamlit

Folium

Geopy

Python 3.8+

## 📎 Example Scenario
Define a drone mission from point A to B between 14:00 and 14:30

The system loads simulated drones and interpolates all paths

Conflicts are detected where paths intersect in space and time

## 🧠 Future Improvements
Altitude-aware path interpolation

Conflict resolution recommendations

Live telemetry data ingestion

Drone fleet control integration

## 📄 License
MIT License

👤 Author
Your Name – Maaz Shahid