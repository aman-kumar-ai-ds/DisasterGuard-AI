import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import html


# ==========================================
# CITY COORDINATES
# ==========================================

CITY_COORDINATES = {
    # Bihar
    "Patna": [25.5941, 85.1376],
    "Muzaffarpur": [26.1209, 85.3647],
    "Ara": [25.5560, 84.6603],
    "Buxar": [25.5647, 83.9777],
    "Gaya": [24.7914, 85.0002],
    "Bhagalpur": [25.2425, 86.9842],
    "Darbhanga": [26.1542, 85.8918],
    "Chapra": [25.7800, 84.7500],
    "Siwan": [26.2196, 84.3567],
    "Purnia": [25.7771, 87.4753],
    "Begusarai": [25.4182, 86.1272],
    "Samastipur": [25.8629, 85.7810],
    "Munger": [25.3748, 86.4735],
    "Kishanganj": [26.0910, 87.9384],
    "Nalanda": [25.1357, 85.4437],
    "Hajipur": [25.6856, 85.2090],
    "Motihari": [26.6470, 84.9060],
    "Sasaram": [24.9490, 84.0314],

    # Other Indian cities
    "Delhi": [28.6139, 77.2090],
    "Jaipur": [26.9124, 75.7873],
    "Mumbai": [19.0760, 72.8777],
    "Kolkata": [22.5726, 88.3639],
    "Chennai": [13.0827, 80.2707],
    "Bengaluru": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Lucknow": [26.8467, 80.9462],
    "Bhopal": [23.2599, 77.4126],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714],
    "Shimla": [31.1048, 77.1734],
    "Dehradun": [30.3165, 78.0322],
    "Guwahati": [26.1445, 91.7362],
    "Srinagar": [34.0837, 74.7973],
    "Visakhapatnam": [17.6868, 83.2185]
}


# ==========================================
# CITY ALIASES
# ==========================================

CITY_ALIASES = {
    "mujjafarpur": "Muzaffarpur",
    "muzafarpur": "Muzaffarpur",
    "mujaffarpur": "Muzaffarpur",
    "muzzaffarpur": "Muzaffarpur",
    "chhapra": "Chapra",
    "bengalore": "Bengaluru"
}


# ==========================================
# SEVERITY COLORS
# ==========================================

COLORS = {
    "Low": "#00E676",
    "Medium": "#2979FF",
    "High": "#FF9100",
    "Critical": "#FF1744"
}


# ==========================================
# FIND CITY COORDINATES
# ==========================================

def find_city_coordinates(location):
    text = str(location or "").strip().lower()

    for alias, correct_name in CITY_ALIASES.items():
        if alias in text:
            return correct_name, CITY_COORDINATES[correct_name]

    for city in sorted(CITY_COORDINATES, key=len, reverse=True):
        if city.lower() in text:
            return city, CITY_COORDINATES[city]

    return None, None


# ==========================================
# MAIN MAP FUNCTION
# ==========================================

def show_disaster_map(incidents):
    incidents = list(incidents or [])

    st.markdown("""
    <style>
    .stApp {
        background-color: #08111f;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #172b46, #0b1729);
        border: 1px solid #355477;
        border-radius: 14px;
        padding: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #b8cbe2 !important;
    }

    div[data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("🌍 Disaster Monitoring Center")
    st.caption("Smart disaster monitoring across India.")

    # SUMMARY
    total = len(incidents)
    critical = sum(1 for x in incidents if len(x) > 4 and x[4] == "Critical")
    high = sum(1 for x in incidents if len(x) > 4 and x[4] == "High")
    active = sum(1 for x in incidents if len(x) > 6 and x[6] == "Active")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", total)
    c2.metric("Critical Incidents", critical)
    c3.metric("High Risk", high)
    c4.metric("Active Incidents", active)

    st.info(f"Total database records received: {total}")

    if not incidents:
        st.warning("No incidents found.")
        return

    # FILTERS
    st.divider()
    st.subheader("Incident Filters")

    f1, f2 = st.columns(2)

    with f1:
        disaster_filter = st.selectbox(
            "Disaster Type",
            ["All", "Flood", "Fire", "Earthquake", "Cyclone", "Landslide"],
            key="dark_map_disaster"
        )

    with f2:
        severity_filter = st.selectbox(
            "Severity",
            ["All", "Low", "Medium", "High", "Critical"],
            key="dark_map_severity"
        )

    # MAP - OpenStreetMap does not require an API key
    disaster_map = folium.Map(
        location=[25.5, 85.0],
        zoom_start=6,
        tiles="OpenStreetMap",
        control_scale=True
    )

    displayed = 0
    unmatched = []
    marker_counts = {}
    marker_locations = []

    # INCIDENT MARKERS
    for incident in incidents:
        if len(incident) < 7:
            continue

        (
            incident_id,
            disaster,
            location,
            people,
            severity,
            description,
            status
        ) = incident[:7]

        if disaster_filter != "All" and disaster != disaster_filter:
            continue

        if severity_filter != "All" and severity != severity_filter:
            continue

        city, base_coords = find_city_coordinates(location)

        if base_coords is None:
            unmatched.append(f"ID {incident_id}: {location}")
            continue

        # Offset markers for incidents in the same city
        marker_number = marker_counts.get(city, 0)
        marker_counts[city] = marker_number + 1

        ring = marker_number // 8 + 1
        angle = (marker_number % 8) * 45
        offset = 0.025 * ring

        coords = [
            base_coords[0] + offset * math.sin(math.radians(angle)),
            base_coords[1] + offset * math.cos(math.radians(angle))
        ]

        color = COLORS.get(severity, "#FFFFFF")

        popup = f"""
        <div style="color:#111; min-width:190px;">
            <b>Incident ID:</b> {html.escape(str(incident_id))}<br>
            <b>Disaster:</b> {html.escape(str(disaster))}<br>
            <b>Location:</b> {html.escape(str(location))}<br>
            <b>Severity:</b> {html.escape(str(severity))}<br>
            <b>Affected People:</b> {html.escape(str(people))}<br>
            <b>Status:</b> {html.escape(str(status))}
        </div>
        """

        # Disaster-specific emoji icon with severity-colored background
        disaster_icons = {
            "Flood": "🌊",
            "Fire": "🔥",
            "Earthquake": "🌍",
            "Cyclone": "🌀",
            "Landslide": "⛰️"
        }

        icon_symbol = disaster_icons.get(str(disaster), "🚨")

        marker_icon = folium.DivIcon(
            html=f"""
            <div style="
                background-color: {color};
                width: 34px;
                height: 34px;
                border: 2px solid white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 19px;
                box-shadow: 0 2px 7px rgba(0,0,0,0.55);
                ">
                {icon_symbol}
            </div>
            """,
            icon_size=(38, 38),
            icon_anchor=(19, 19)
        )

        folium.Marker(
            location=coords,
            icon=marker_icon,
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"ID {incident_id} | {disaster} | {location}"
        ).add_to(disaster_map)

        marker_locations.append(coords)
        displayed += 1

    # AUTOMATIC ZOOM TO ALL VISIBLE INCIDENTS
    if len(marker_locations) >= 2:
        disaster_map.fit_bounds(marker_locations, padding=[40, 40])
    elif len(marker_locations) == 1:
        disaster_map.location = marker_locations[0]
        disaster_map.zoom_start = 10

    # DISPLAY MAP
    st.divider()
    st.subheader("📍 Disaster Location Map")

    st_folium(
        disaster_map,
        height=600,
        width=1000,
        returned_objects=[],
        key="disaster_guard_dark_map"
    )

    st.success(f"Mapped incidents: {displayed} / {total}")

    if unmatched:
        st.warning(
            "Some locations could not be mapped:\n\n" + "\n".join(unmatched)
        )

    # LEGENDS
    st.markdown("""
    ### Disaster Type Legend

    🌊 Flood &nbsp;&nbsp;
    🔥 Fire &nbsp;&nbsp;
    🌍 Earthquake &nbsp;&nbsp;
    🌀 Cyclone &nbsp;&nbsp;
    ⛰️ Landslide

    ### Severity Legend

    🟢 Low &nbsp;&nbsp;
    🔵 Medium &nbsp;&nbsp;
    🟠 High &nbsp;&nbsp;
    🔴 Critical
    """, unsafe_allow_html=True)

    st.caption(
        "Academic demonstration. City markers use predefined "
        "coordinates, not live GPS tracking."
    )
