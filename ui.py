import streamlit as st
import re
import pandas as pd
from vait import get_travel_info

# Set page configuration
st.set_page_config(
    page_title="Travel Guide & Map Viewer",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .header-text {
        color: #2c3e50;
        font-size: 2.5em;
        text-align: center;
        padding: 20px;
    }
    .stMarkdown {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .map-container {
        margin-top: 30px;
        border-radius: 15px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="header-text">✈️ Smart Travel Planner</p>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([3, 2])
with col1:
    destination = st.text_input("**Enter Destination**", placeholder="Where would you like to go? (e.g., Istanbul, Paris)")
with col2:
    travel_type = st.selectbox(
        "**Travel Type**",
        ["couple", "family", "friends", "business", "bachelor", "general"],
        index=2
    )

if st.button("**Generate Travel Plan**", use_container_width=True):
    if not destination:
        st.error("Please enter a destination to continue")
    else:
        with st.spinner("Creating your personalized travel experience..."):
            # Get travel information
            travel_info = get_travel_info(destination, travel_type)
            
            # Parse coordinates from the generated content
            lat_lon_pattern = re.compile(r"Latitude ([\d.]+), Longitude ([\d.]+)")
            matches = lat_lon_pattern.findall(travel_info)
            
            # Display results
            with st.container():
                st.markdown("---")
                col_info, col_map = st.columns([5, 5])
                
                with col_info:
                    with st.expander(f"**{destination.capitalize()} Travel Guide**", expanded=True):
                        st.markdown(travel_info)
                
                with col_map:
                    if matches:
                        st.subheader("🗺️ Interactive Travel Map")
                        df = pd.DataFrame(matches, columns=['lat', 'lon'])
                        df['lat'] = df['lat'].astype(float)
                        df['lon'] = df['lon'].astype(float)
                        st.map(df, use_container_width=True)
                    else:
                        st.warning("No location data available for mapping")