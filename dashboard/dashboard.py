from pathlib import Path
import sqlite3
import time

import pandas as pd
import streamlit as st
import pydeck as pdk
import streamlit.components.v1 as components

# --------- PATHS & CONSTANTS ---------

# Path to traffic.db in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "traffic.db"

INTERSECTION_ID = "intersection1"

# Approximate coordinates for Conlin Rd & Simcoe St N (North Oshawa / Ontario Tech)
INTERSECTION_LAT = 43.9456
INTERSECTION_LON = -78.8965

# Google Maps link for embedded view
GOOGLE_MAPS_EMBED_URL = (
    "https://www.google.com/maps?q="
    f"{INTERSECTION_LAT},{INTERSECTION_LON}"
    "&hl=en&z=17&output=embed"
)


# --------- DB HELPERS ---------

@st.cache_resource
def get_db_connection():
    # cache the connection across reruns
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def load_samples(limit: int = 200):
    conn = get_db_connection()
    query = """
        SELECT id, ts_utc, intersection_id, avg_speed, vehicle_count,
               congestion_score, congestion_level, is_anomaly
        FROM traffic_samples
        WHERE intersection_id = ?
        ORDER BY id DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(INTERSECTION_ID, limit))
    if not df.empty:
        df = df.iloc[::-1]  # chronological order
    return df


# --------- COLOR HELPERS ---------

def congestion_color_rgb(level: str):
    """[R,G,B] for PyDeck marker."""
    level = str(level).lower()
    if level == "green":
        return [0, 200, 83]      # green
    elif level == "yellow":
        return [255, 214, 0]     # yellow
    elif level == "orange":
        return [255, 145, 0]     # orange
    else:
        return [213, 0, 0]       # red


def congestion_color_hex(level: str):
    """Hex color for HTML background."""
    level = str(level).lower()
    if level == "green":
        return "#00c853"
    elif level == "yellow":
        return "#ffd600"
    elif level == "orange":
        return "#ff9100"
    else:
        return "#d50000"


# --------- MAIN APP ---------

def main():
    st.set_page_config(
        page_title="Smart Traffic Mini – Intersection Dashboard",
        layout="wide",
    )

    # Small CSS tweak to hide the fullscreen button on charts/maps
    st.markdown(
        """
        <style>
        button[title="View fullscreen"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title(" Smart Traffic Mini – Intersection 1")
    st.write(
        "Real-time view of simulated traffic conditions with congestion "
        "and anomaly detection."
    )

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        refresh_sec = st.slider(
            "Auto-refresh every (seconds)",
            min_value=2,
            max_value=15,
            value=5,
        )
        sample_limit = st.slider(
            "Number of recent samples to display",
            min_value=50,
            max_value=500,
            value=200,
        )
        st.caption(f"Dashboard auto-refresh: every {refresh_sec} seconds")
        st.markdown(
            """
            **Color legend**  
             Free / light traffic  
             Moderate  
             Heavy  
             Severe / likely congestion
            """
        )

    df = load_samples(limit=sample_limit)

    if df.empty:
        st.warning("No data yet. Make sure simulator and processor are running.")
        st.stop()

    latest = df.iloc[-1]
    level = latest["congestion_level"]
    bg_hex = congestion_color_hex(level)

    # ---------- INTERSECTION STATUS PANEL (color background) ----------

    st.markdown(
        f"""
        <div style="
            padding: 18px;
            border-radius: 16px;
            background-color: {bg_hex};
            color: white;
            margin-bottom: 18px;
        ">
            <h2 style="margin: 0 0 6px 0;">Intersection 1 Status: {level}</h2>
            <p style="margin: 0;">
                <strong>Speed:</strong> {latest['avg_speed']:.1f} km/h &nbsp; | &nbsp;
                <strong>Vehicles/sec:</strong> {latest['vehicle_count']} &nbsp; | &nbsp;
                <strong>Anomaly:</strong> {"Yes" if int(latest["is_anomaly"]) == 1 else "No"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- CHARTS + LIVE MAP LAYOUT ----------

    chart_col, map_col = st.columns([3, 2])

    with chart_col:
        st.subheader("Speed over Time")
        st.line_chart(
            df.set_index("ts_utc")[["avg_speed"]],
            height=250,
        )

        st.subheader("Vehicle Count over Time")
        st.line_chart(
            df.set_index("ts_utc")[["vehicle_count"]],
            height=250,
        )

    with map_col:
        st.subheader("Live Simulation – Conlin Rd & Simcoe St N")
        st.markdown(
            "📍 **Conlin Rd & Simcoe St N – Oshawa (Ontario Tech North Campus area)**",
        )

        # Single marker representing the intersection, color-coded
        map_df = pd.DataFrame(
            {
                "lat": [INTERSECTION_LAT],
                "lon": [INTERSECTION_LON],
                "congestion_level": [level],
                "avg_speed": [latest["avg_speed"]],
                "veh_per_sec": [latest["vehicle_count"]],
            }
        )

        # Radius grows with congestion_score (0–1) → 80–300
        max_radius = 300
        min_radius = 80
        congestion_score = float(latest["congestion_score"])
        radius = min_radius + (max_radius - min_radius) * congestion_score

        marker_rgb = congestion_color_rgb(level)

        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=INTERSECTION_LAT,
                longitude=INTERSECTION_LON,
                zoom=16,
                pitch=40,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position="[lon, lat]",
                    get_radius=radius,
                    get_fill_color=marker_rgb,   # [R, G, B]
                    pickable=True,
                )
            ],
            tooltip={
                "text": "Level: {congestion_level}\n"
                        "Speed: {avg_speed} km/h\n"
                        "Flow: {veh_per_sec} veh/s"
            },
        )

        st.pydeck_chart(deck, use_container_width=True, height=320)

    # ---------- EMBEDDED GOOGLE MAP (REAL VIEW) ----------

    st.subheader("Real Intersection View – Google Maps")
    st.write(
        "This embedded map shows the actual Conlin Rd & Simcoe St N intersection "
        "in Google Maps, matching the simulated intersection above."
    )

    components.html(
        f"""
        <iframe
            width="100%"
            height="420"
            frameborder="0" style="border:0"
            referrerpolicy="no-referrer-when-downgrade"
            src="{GOOGLE_MAPS_EMBED_URL}"
            allowfullscreen>
        </iframe>
        """,
        height=430,
    )

    # Auto-refresh: sleep then rerun
    time.sleep(refresh_sec)
    st.rerun()


if __name__ == "__main__":
    main()
