"""SIH26001 Landslide Early Warning System dashboard."""

from __future__ import annotations

import folium
import streamlit as st
from streamlit_folium import st_folium


GUWAHATI = (26.1445, 91.7362)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(value, maximum))


def assess_risk(rainfall: int, slope_angle: int, soil_moisture: int) -> dict[str, object]:
    """Convert the three sensor inputs into a transparent risk assessment."""

    rainfall_risk = clamp(rainfall / 250)
    slope_risk = clamp((slope_angle - 15) / 35)
    moisture_risk = clamp((soil_moisture - 25) / 65)
    risk_score = round(
        (rainfall_risk * 0.45 + slope_risk * 0.30 + moisture_risk * 0.25) * 100
    )

    if risk_score < 30:
        return {
            "label": "Safe",
            "color": "green",
            "score": risk_score,
            "message": "Current conditions are within the safe operating range.",
        }
    if risk_score < 55:
        return {
            "label": "Watch",
            "color": "beige",
            "score": risk_score,
            "message": "Keep monitoring conditions for changes in rainfall or soil moisture.",
        }
    if risk_score < 75:
        return {
            "label": "Warning",
            "color": "orange",
            "score": risk_score,
            "message": "Conditions indicate elevated landslide risk. Prepare local response teams.",
        }
    return {
        "label": "Critical Alert",
        "color": "red",
        "score": risk_score,
        "message": "Critical conditions detected. Issue an early warning and start evacuation protocols.",
    }


def build_map(status: dict[str, object]) -> folium.Map:
    """Build the live Guwahati alert map."""

    risk_color = str(status["color"])
    score = int(status["score"])
    label = str(status["label"])

    map_view = folium.Map(
        location=GUWAHATI,
        zoom_start=11,
        control_scale=True,
        tiles="OpenStreetMap",
    )
    folium.Circle(
        location=GUWAHATI,
        radius=1800 + score * 18,
        color=risk_color,
        weight=2,
        fill=True,
        fill_color=risk_color,
        fill_opacity=0.18,
        tooltip=f"{label} zone · risk score {score}/100",
    ).add_to(map_view)
    folium.Marker(
        location=GUWAHATI,
        tooltip=f"{label} · Guwahati monitoring station",
        popup=folium.Popup(
            f"<b>SIH26001 Monitoring Station</b><br>"
            f"Guwahati, Assam<br>"
            f"Alert level: <b>{label}</b><br>"
            f"Risk score: {score}/100",
            max_width=280,
        ),
        icon=folium.Icon(color=risk_color, icon="warning-sign", prefix="glyphicon"),
    ).add_to(map_view)
    return map_view


st.set_page_config(
    page_title="SIH26001 · Landslide Early Warning",
    page_icon="⛰️",
    layout="wide",
)

st.title("SIH26001 Landslide Early Warning System")
st.caption("Interactive situational dashboard for the Guwahati monitoring zone")

with st.sidebar:
    st.header("Sensor inputs")
    st.write("Adjust the simulated field readings to update the alert state.")
    rainfall = st.slider(
        "24-hour rainfall (mm)",
        min_value=0,
        max_value=300,
        value=45,
        step=5,
        help="Accumulated rainfall recorded during the last 24 hours.",
    )
    slope_angle = st.slider(
        "Slope angle (°)",
        min_value=0,
        max_value=60,
        value=18,
        step=1,
        help="Average terrain slope angle at the monitored location.",
    )
    soil_moisture = st.slider(
        "Soil moisture (%)",
        min_value=0,
        max_value=100,
        value=38,
        step=1,
        help="Volumetric soil moisture reading from the sensor array.",
    )
    st.divider()
    st.caption("Prototype mode · readings are simulated")

status = assess_risk(rainfall, slope_angle, soil_moisture)
label = str(status["label"])
score = int(status["score"])

left, right = st.columns([1.3, 1], gap="large")
with left:
    st.subheader("Live alert map")
    st_folium(
        build_map(status),
        use_container_width=True,
        height=500,
        returned_objects=[],
    )

with right:
    st.subheader("Current status")
    message = f"**{label}** · risk score {score}/100"
    if label == "Safe":
        st.success(message)
    elif label == "Watch":
        st.info(message)
    elif label == "Warning":
        st.warning(message)
    else:
        st.error(message)
    st.write(str(status["message"]))

    st.metric("Rainfall", f"{rainfall} mm", help="24-hour cumulative rainfall")
    st.metric("Slope angle", f"{slope_angle}°")
    st.metric("Soil moisture", f"{soil_moisture}%")

st.divider()
st.subheader("Risk model")
st.write(
    "The prototype combines rainfall, terrain slope, and soil moisture into a "
    "weighted risk score. Move any slider to see the Guwahati marker and alert "
    "status respond immediately."
)
metric_a, metric_b, metric_c = st.columns(3)
with metric_a:
    st.progress(clamp(rainfall / 250), text="Rainfall contribution")
with metric_b:
    st.progress(clamp((slope_angle - 15) / 35), text="Slope contribution")
with metric_c:
    st.progress(clamp((soil_moisture - 25) / 65), text="Moisture contribution")
