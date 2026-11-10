# put streamlit code here as needed
import altair as alt
import pandas as pd
import streamlit as st


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

US_TOPO_URL = "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json"
states = alt.topo_feature(US_TOPO_URL, "states")
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
    "**Write-up For Visualization 1.**This map shows where sightings cluster geographically,"
    "showing concentrations in the Pacific Northwest, Great Lakes, and Appalachia, and"
    "I used small transparent circles on a light gray base map of the United States with orange/green pair for Class A vs. Class B, "
    "and a season multiselect and clickable legend for filtering. Given more time, I would add a density layer to reduce overplotting "
    "in crowded areas and maybe like a zoom in feature where you can focus in on certain regions."
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
    "**Write-up For Visualization 2. This chart shows which states have the most reports "
   " and how summer dominates across states, "
   " using horizontal bars sorted by total, a zero baseline, intuitive season colors, "
   " and a slider and radio button to control the number of states and classification. "
   " Given more time, I would normalize counts by population or land area so large states don’t dominate and add "
  "  a year filter to show how reporting changes over time."
)

