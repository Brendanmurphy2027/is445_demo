# put streamlit code here as needed
import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data as vega_data

def load_data():
    df = pd.read_csv("bfro_reports_fall2022.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

df = load_data()

st.title("Bigfoot Field Researchers Organization Sightings")
st.write(
    f"This report explores {len(df):,} BFRO sighting reports. Class A reports are clear, "
    "close-range sightings; Class B reports are less clear or more distant; Class C reports "
    "are second-hand or unverifiable."
)

st.header("Visualization 1 - Where are sightings reported?")

geo = df.dropna(subset=["latitude", "longitude"])
geo = geo[geo["classification"].isin(["Class A", "Class B"])]
geo = geo[(geo.longitude.between(-125, -66)) & (geo.latitude.between(24, 50))]

seasons = st.multiselect(
    "Seasons to show",
    ["Spring", "Summer", "Fall", "Winter"],
    default = ["Spring", "Summer", "Fall", "Winter"]
)
geo = geo[geo["season"].isin(seasons)]

states = alt.topo_feature(vega_data.us_10m.url, "states")
base = (
    alt.Chart(states)
    .mark_geoshape(fill="#f2f2f2", stroke="white")
    .project("albersUsa")
    .properties(width=800, height=500)
)

legend_sel = alt.selection_point(fields=["classification"], bind="legend")
points = (
    alt.Chart(geo)
    .mark_circle(size=25)
    .encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        color=alt.Color(
            "classification:N",
            title="Classification (click to filter)",
            scale=alt.Scale(domain=["Class A", "Class B"], range=["#d95f02", "#1b9e77"]),
        ),
        opacity=alt.condition(legend_sel, alt.value(0.7), alt.value(0.05)),
        tooltip=["state", "county", "date:T", "season", "classification"],
    )
    .add_params(legend_sel)
)
st.altair_chart(base + points)

st.write(
    "**Write-up (Viz 1).** TODO: describe what you highlight (geographic clustering in the "
    "Pacific Northwest, Great Lakes, and Appalachia), your design choices (light gray base map "
    "so points stand out, small semi-transparent circles to reduce overplotting, a "
    "colorblind-safe orange/green pair for Class A vs. B, Albers USA projection), the "
    "interactivity (season multiselect and clickable legend), and what you would change with "
    "more time (e.g., a density layer, handling Alaska/Hawaii, linking to Viz 2)."
)

st.header("Visualization 2: Which states have the most reports?")

c1, c2 = st.columns(2)
top_n = c1.slider("Number of states", 5, 25, 15)
cls = c2.radio("Classification", ["All", "Class A", "Class B"], horizontal=True)

d2 = df if cls == "All" else df[df["classification"] == cls]
d2 = d2[d2["season"] != "Unknown"]
top_states = d2["state"].value_counts().head(top_n).index.tolist()
d2 = d2[d2["state"].isin(top_states)]
counts = d2.groupby(["state", "season"]).size().reset_index(name="reports")

bars = (
    alt.Chart(counts)
    .mark_bar()
    .encode(
        y=alt.Y("state:N", sort="-x", title=None),
        x=alt.X("reports:Q", title="Number of reports"),
        color=alt.Color(
            "season:N",
            sort=["Spring", "Summer", "Fall", "Winter"],
            scale=alt.Scale(
                domain=["Spring", "Summer", "Fall", "Winter"],
                range=["#66a61e", "#e6ab02", "#d95f02", "#386cb0"],
            ),
        ),
        order=alt.Order("season:N"),
        tooltip=["state", "season", "reports"],
    )
    .properties(height=25 * top_n + 40)
)
st.altair_chart(bars)

st.write(
    "**Write-up (Viz 2).** TODO: describe what you highlight (Washington, California, Florida "
    "lead; summer dominates), design choices (horizontal bars sorted by total for readable "
    "state names, stacked by season with intuitive season colors, zero baseline), the widgets "
    "(slider for how many states, radio for classification), and what you would change "
    "(normalize by population or land area, add a year filter)."
)

