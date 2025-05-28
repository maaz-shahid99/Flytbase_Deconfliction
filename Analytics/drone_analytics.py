import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
from collections import defaultdict
import json

class DroneCollisionAnalytics:
    def __init__(self, conflicts_data, drones_data):
        """
        Initialize with conflict detection results and drone flight data
        """
        self.conflicts = conflicts_data
        self.drones = drones_data
        self.df_conflicts = self._prepare_conflicts_dataframe()
        
    def _prepare_conflicts_dataframe(self):
        """Convert conflicts to pandas DataFrame for analysis"""
        if not self.conflicts:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.conflicts)
        df['time_dt'] = pd.to_datetime(df['time'], format='%H:%M')
        df['hour'] = df['time_dt'].dt.hour
        df['minute'] = df['time_dt'].dt.minute
        return df
    
    def conflict_frequency_analysis(self):
        """Analyze conflict frequency over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Conflicts by time of day
        if not self.df_conflicts.empty:
            time_counts = self.df_conflicts['time'].value_counts().sort_index()
            ax1.bar(time_counts.index, time_counts.values, color='red', alpha=0.7)
            ax1.set_title('Conflicts by Time Period')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Number of Conflicts')
            ax1.tick_params(axis='x', rotation=45)
            
            # Conflicts by drone
            drone_counts = self.df_conflicts['drone'].value_counts()
            ax2.bar(drone_counts.index, drone_counts.values, color='orange', alpha=0.7)
            ax2.set_title('Conflicts by Drone ID')
            ax2.set_xlabel('Drone ID')
            ax2.set_ylabel('Number of Conflicts')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, 'No Conflicts Detected', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=16)
            ax2.text(0.5, 0.5, 'No Conflicts Detected', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=16)
        
        plt.tight_layout()
        return fig
    
    def distance_distribution_analysis(self):
        """Analyze distribution of conflict distances"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        if not self.df_conflicts.empty:
            # 3D Distance Distribution
            distances_3d = self.df_conflicts['distance_3d_m']
            ax1.hist(distances_3d, bins=20, color='blue', alpha=0.7, edgecolor='black')
            ax1.set_title('3D Distance Distribution')
            ax1.set_xlabel('Distance (meters)')
            ax1.set_ylabel('Frequency')
            ax1.axvline(distances_3d.mean(), color='red', linestyle='--', 
                       label=f'Mean: {distances_3d.mean():.1f}m')
            ax1.legend()
            
            # Horizontal vs Vertical Distance Scatter
            if 'horizontal_distance_m' in self.df_conflicts.columns:
                ax2.scatter(self.df_conflicts['horizontal_distance_m'], 
                           self.df_conflicts['vertical_distance_m'], 
                           c=distances_3d, cmap='viridis', alpha=0.7)
                ax2.set_xlabel('Horizontal Distance (m)')
                ax2.set_ylabel('Vertical Distance (m)')
                ax2.set_title('Horizontal vs Vertical Separation')
                cbar = plt.colorbar(ax2.collections[0], ax=ax2)
                cbar.set_label('3D Distance (m)')
            
            # Distance vs Time
            time_numeric = self.df_conflicts['hour'] + self.df_conflicts['minute']/60
            ax3.scatter(time_numeric, distances_3d, color='red', alpha=0.7)
            ax3.set_xlabel('Time (Hours)')
            ax3.set_ylabel('3D Distance (m)')
            ax3.set_title('Conflict Distance vs Time')
            
            # Box plot of distances by drone
            drone_distances = []
            drone_labels = []
            for drone in self.df_conflicts['drone'].unique():
                drone_data = self.df_conflicts[self.df_conflicts['drone'] == drone]
                drone_distances.append(drone_data['distance_3d_m'].values)
                drone_labels.append(drone)
            
            ax4.boxplot(drone_distances, labels=drone_labels)
            ax4.set_title('Distance Distribution by Drone')
            ax4.set_xlabel('Drone ID')
            ax4.set_ylabel('3D Distance (m)')
            ax4.tick_params(axis='x', rotation=45)
            
        else:
            for ax in [ax1, ax2, ax3, ax4]:
                ax.text(0.5, 0.5, 'No Conflicts for Analysis', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def risk_heatmap_analysis(self):
        """Create risk heatmap based on time and location"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        if not self.df_conflicts.empty:
            # Time-based risk heatmap
            hour_minute_conflicts = self.df_conflicts.groupby(['hour', 'minute']).size().reset_index(name='conflicts')
            pivot_time = hour_minute_conflicts.pivot(index='minute', columns='hour', values='conflicts').fillna(0)
            
            sns.heatmap(pivot_time, annot=True, cmap='Reds', ax=ax1, fmt='g')
            ax1.set_title('Conflict Risk Heatmap (Hour vs Minute)')
            ax1.set_xlabel('Hour')
            ax1.set_ylabel('Minute')
            
            # Spatial risk heatmap (if location data available)
            if 'location' in self.df_conflicts.columns:
                lats = [loc[0] for loc in self.df_conflicts['location']]
                lons = [loc[1] for loc in self.df_conflicts['location']]
                
                # Create 2D histogram for spatial distribution
                h, xedges, yedges = np.histogram2d(lats, lons, bins=10)
                extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
                
                im = ax2.imshow(h, extent=extent, origin='lower', cmap='Reds', aspect='auto')
                ax2.set_title('Spatial Conflict Heatmap')
                ax2.set_xlabel('Longitude')
                ax2.set_ylabel('Latitude')
                plt.colorbar(im, ax=ax2, label='Conflict Count')
        else:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, 'No Conflicts for Heatmap', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def threshold_sensitivity_analysis(self, threshold_range=range(10, 101, 10)):
        """Analyze how conflict detection changes with different thresholds"""
        # This would require re-running conflict detection with different thresholds
        # For demo, we'll simulate the analysis
        
        conflict_counts = []
        thresholds = list(threshold_range)
        
        # Simulate: higher thresholds = more conflicts detected
        for thresh in thresholds:
            # In real implementation, you'd call check_unified_conflicts with different thresholds
            simulated_count = len(self.conflicts) * (thresh / 50.0)  # Normalize to current threshold
            conflict_counts.append(int(simulated_count))
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.plot(thresholds, conflict_counts, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Horizontal Threshold (meters)')
        ax.set_ylabel('Number of Conflicts Detected')
        ax.set_title('Threshold Sensitivity Analysis')
        ax.grid(True, alpha=0.3)
        
        # Add annotations for key points
        max_idx = np.argmax(conflict_counts)
        ax.annotate(f'Peak: {thresholds[max_idx]}m\n({conflict_counts[max_idx]} conflicts)', 
                   xy=(thresholds[max_idx], conflict_counts[max_idx]),
                   xytext=(thresholds[max_idx]+15, conflict_counts[max_idx]+2),
                   arrowprops=dict(arrowstyle='->', color='red'))
        
        plt.tight_layout()
        return fig
    
    def drone_traffic_density_analysis(self):
        """Analyze drone traffic density over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Create time series of active drones
        time_slots = []
        active_counts = []
        
        # Parse all drone mission times
        all_times = set()
        for drone in self.drones:
            all_times.update(drone['times'])
        
        sorted_times = sorted(all_times, key=lambda x: datetime.strptime(x, '%H:%M'))
        
        for time_slot in sorted_times:
            time_dt = datetime.strptime(time_slot, '%H:%M')
            active_count = 0
            
            for drone in self.drones:
                drone_times = [datetime.strptime(t, '%H:%M') for t in drone['times']]
                if min(drone_times) <= time_dt <= max(drone_times):
                    active_count += 1
            
            time_slots.append(time_slot)
            active_counts.append(active_count)
        
        # Traffic density over time
        ax1.plot(time_slots, active_counts, marker='o', linewidth=2, markersize=6, color='blue')
        ax1.fill_between(time_slots, active_counts, alpha=0.3, color='blue')
        ax1.set_title('Drone Traffic Density Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Number of Active Drones')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Conflict rate vs traffic density
        if not self.df_conflicts.empty:
            conflict_times = self.df_conflicts['time'].tolist()
            conflict_rates = []
            
            for time_slot in time_slots:
                conflicts_at_time = conflict_times.count(time_slot)
                active_at_time = active_counts[time_slots.index(time_slot)]
                rate = conflicts_at_time / max(active_at_time, 1)  # Avoid division by zero
                conflict_rates.append(rate)
            
            ax2.scatter(active_counts, conflict_rates, alpha=0.7, color='red', s=60)
            ax2.set_xlabel('Number of Active Drones')
            ax2.set_ylabel('Conflicts per Drone')
            ax2.set_title('Conflict Rate vs Traffic Density')
            ax2.grid(True, alpha=0.3)
            
            # Add trend line
            z = np.polyfit(active_counts, conflict_rates, 1)
            p = np.poly1d(z)
            ax2.plot(active_counts, p(active_counts), "r--", alpha=0.8, 
                    label=f'Trend: y={z[0]:.3f}x+{z[1]:.3f}')
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, 'No Conflicts for Rate Analysis', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def generate_statistical_summary(self):
        """Generate comprehensive statistical summary"""
        if self.df_conflicts.empty:
            return {
                'total_conflicts': 0,
                'summary': 'No conflicts detected in the current scenario.'
            }
        
        stats = {
            'total_conflicts': len(self.df_conflicts),
            'unique_drones_involved': self.df_conflicts['drone'].nunique(),
            'time_span': f"{self.df_conflicts['time'].min()} - {self.df_conflicts['time'].max()}",
            'average_3d_distance': self.df_conflicts['distance_3d_m'].mean(),
            'min_3d_distance': self.df_conflicts['distance_3d_m'].min(),
            'max_3d_distance': self.df_conflicts['distance_3d_m'].max(),
            'std_3d_distance': self.df_conflicts['distance_3d_m'].std(),
            'most_conflict_prone_drone': self.df_conflicts['drone'].mode().iloc[0],
            'peak_conflict_time': self.df_conflicts['time'].mode().iloc[0] if not self.df_conflicts['time'].mode().empty else 'N/A'
        }
        
        return stats


# Example usage function
def analyze_drone_conflicts(conflicts_data, drones_data):
    """
    Main function to run all analyses
    Usage:
    conflicts = check_unified_conflicts(primary, others, 50, 25)
    figures = analyze_drone_conflicts(conflicts, drones_data)
    """
    analyzer = DroneCollisionAnalytics(conflicts_data, drones_data)
    
    figures = {
        'frequency': analyzer.conflict_frequency_analysis(),
        'distances': analyzer.distance_distribution_analysis(), 
        'heatmap': analyzer.risk_heatmap_analysis(),
        'sensitivity': analyzer.threshold_sensitivity_analysis(),
        'traffic': analyzer.drone_traffic_density_analysis()
    }
    
    stats = analyzer.generate_statistical_summary()
    
    return figures, stats

# Integration example for your Streamlit app
def add_analytics_to_streamlit(conflicts, drones):
    """
    Add this to your app.py to include analytics
    """
    import streamlit as st
    
    if conflicts:
        st.header("📊 Conflict Analytics")
        
        analyzer = DroneCollisionAnalytics(conflicts, drones)
        
        # Statistical summary
        stats = analyzer.generate_statistical_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Conflicts", stats['total_conflicts'])
        with col2:
            st.metric("Avg Distance", f"{stats['average_3d_distance']:.1f}m")
        with col3:
            st.metric("Min Distance", f"{stats['min_3d_distance']:.1f}m")
        with col4:
            st.metric("Drones Involved", stats['unique_drones_involved'])
        
        # Generate and display plots
        tab1, tab2, tab3, tab4 = st.tabs(["Frequency", "Distances", "Risk Heatmap", "Traffic"])
        
        with tab1:
            fig = analyzer.conflict_frequency_analysis()
            st.pyplot(fig)
        
        with tab2:
            fig = analyzer.distance_distribution_analysis()
            st.pyplot(fig)
            
        with tab3:
            fig = analyzer.risk_heatmap_analysis()
            st.pyplot(fig)
            
        with tab4:
            fig = analyzer.drone_traffic_density_analysis()
            st.pyplot(fig)