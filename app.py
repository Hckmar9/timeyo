import streamlit as st
import pandas as pd
import datetime
import pytz
import plotly.express as px
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import os
import json

st.set_page_config(
    page_title="Global Time Zone Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOCATIONS_FILE = "saved_locations.json"

def load_saved_locations():
    if os.path.exists(LOCATIONS_FILE):
        try:
            with open(LOCATIONS_FILE, "r") as file:
                return json.load(file)
        except Exception as e:
            st.sidebar.error(f"Error loading saved locations: {e}")
    return {
        "Mexico City (Mexico)": {"country": "Mexico", "state": "Mexico City", "latitude": 19.4326, "longitude": -99.1332},
        "Cancun (Mexico)": {"country": "Mexico", "state": "Quintana Roo", "latitude": 21.1619, "longitude": -86.8515},
        "Hermosillo (Mexico)": {"country": "Mexico", "state": "Sonora", "latitude": 29.0729, "longitude": -110.9559},
        "Tijuana (Mexico)": {"country": "Mexico", "state": "Baja California", "latitude": 32.5149, "longitude": -117.0382},
        "New York (USA)": {"country": "United States", "state": "New York", "latitude": 40.7128, "longitude": -74.0060},
        "Los Angeles (USA)": {"country": "United States", "state": "California", "latitude": 34.0522, "longitude": -118.2437},
        "Tokyo (Japan)": {"country": "Japan", "state": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
        "London (UK)": {"country": "United Kingdom", "state": "England", "latitude": 51.5074, "longitude": -0.1278},
    }

def save_locations(locations):
    try:
        with open(LOCATIONS_FILE, "w") as file:
            json.dump(locations, file)
        return True
    except Exception as e:
        st.sidebar.error(f"Error saving locations: {e}")
        return False

st.title("🌍 Global Time Zone Dashboard")
st.markdown("""
This dashboard shows the current local time across different regions, accounting for daylight saving time
and regional time policies. Perfect for international coordination and travel planning.
""")

if 'predefined_locations' not in st.session_state:
    st.session_state.predefined_locations = load_saved_locations()

if 'selected_locations' not in st.session_state:
    st.session_state.selected_locations = ["Mexico City (Mexico)", "Tijuana (Mexico)"]

st.sidebar.header("Settings")

with st.sidebar.expander("Add Custom Location"):
    custom_country = st.text_input("Country")
    custom_state = st.text_input("State/Province/Region")
    custom_city = st.text_input("City")

    if st.button("Add Location"):
        if custom_country and custom_city:
            geolocator = Nominatim(user_agent="timezone_dashboard")

            if custom_state:
                location_str = f"{custom_city}, {custom_state}, {custom_country}"
            else:
                location_str = f"{custom_city}, {custom_country}"

            try:
                location = geolocator.geocode(location_str)

                if not location and custom_state:
                    location_str = f"{custom_city}, {custom_country}"
                    location = geolocator.geocode(location_str)

                if location:
                    new_location = {
                        "country": custom_country,
                        "state": custom_state if custom_state else "",
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    }

                    location_key = f"{custom_city} ({custom_country})"

                    st.session_state.predefined_locations[location_key] = new_location

                    save_locations(st.session_state.predefined_locations)

                    st.sidebar.success(f"Added {custom_city}. It is now available to select and has been saved.")
                else:
                    st.sidebar.error(f"Location not found: {location_str}")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

st.session_state.selected_locations = [loc for loc in st.session_state.selected_locations
                                       if loc in st.session_state.predefined_locations]

selected_locations = st.sidebar.multiselect(
    "Select locations to display",
    options=list(st.session_state.predefined_locations.keys()),
    default=st.session_state.selected_locations
)

st.session_state.selected_locations = selected_locations

def get_timezone(lat, lng):
    tf = TimezoneFinder()
    return tf.timezone_at(lng=lng, lat=lat)

def get_time_info(location_data):
    timezone_str = get_timezone(location_data["latitude"], location_data["longitude"])
    if not timezone_str:
        return None

    timezone = pytz.timezone(timezone_str)
    now_utc = datetime.datetime.now(pytz.UTC)
    local_time = now_utc.astimezone(timezone)

    standard_offset = timezone._transition_info[0][0]
    standard_time = now_utc.replace(tzinfo=pytz.UTC) + standard_offset

    is_dst = local_time.dst() != datetime.timedelta(0)

    return {
        "timezone": timezone_str,
        "local_time": local_time,
        "standard_time": standard_time,
        "is_dst": is_dst,
        "dst_offset": local_time.dst(),
        "utc_offset": local_time.utcoffset(),
        "standard_offset": standard_offset
    }

st.header("Current Local Times")

time_data = []
for location_name in selected_locations:
    location_data = st.session_state.predefined_locations[location_name]
    time_info = get_time_info(location_data)

    if time_info:
        display_name = location_name.split(" (")[0]

        time_data.append({
            "Location": display_name,
            "Country/Region": f"{location_data['state']}, {location_data['country']}",
            "Local Time": time_info["local_time"].strftime("%H:%M:%S"),
            "Date": time_info["local_time"].strftime("%Y-%m-%d"),
            "Time Zone": time_info["timezone"],
            "DST Active": "Yes" if time_info["is_dst"] else "No",
            "UTC Offset": str(time_info["utc_offset"]),
            "Standard Time": time_info["standard_time"].strftime("%H:%M:%S")
        })

if time_data:
    time_df = pd.DataFrame(time_data)
    st.dataframe(time_df, hide_index=True)
else:
    st.info("Please select locations to display their time information.")

st.header("World Map View")

m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

for location_name in selected_locations:
    location_data = st.session_state.predefined_locations[location_name]
    time_info = get_time_info(location_data)

    if time_info:
        popup_text = f"""
        <b>{location_name}</b><br>
        Local time: {time_info['local_time'].strftime('%H:%M:%S')}<br>
        Date: {time_info['local_time'].strftime('%Y-%m-%d')}<br>
        Time Zone: {time_info['timezone']}<br>
        DST Active: {"Yes" if time_info['is_dst'] else "No"}<br>
        UTC Offset: {str(time_info['utc_offset'])}<br>
        Standard Time: {time_info['standard_time'].strftime('%H:%M:%S')}
        """

        hour = time_info['local_time'].hour
        if 6 <= hour < 18:
            marker_color = "blue"
        else:
            marker_color = "darkblue"

        folium.Marker(
            location=[location_data["latitude"], location_data["longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{location_name}: {time_info['local_time'].strftime('%H:%M')}",
            icon=folium.Icon(color=marker_color, icon="clock", prefix="fa")
        ).add_to(m)

folium_static(m, width=1200)

st.markdown("---")
st.markdown("""
**Note:** This dashboard displays time information based on the IANA Time Zone Database.
Time policies may change, and this tool should be used as a reference only.
""")

# Shhht.. 208 lines of code... I can do better than this... 😅