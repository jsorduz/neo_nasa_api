import pandas as pd
import streamlit as st

from logger import logger
from services.nasa import get_neo, get_neo_by_id


@st.cache_data
def load_neo():
    neo_data = get_neo()["near_earth_objects"]
    # API data has format {<day>: <list_of_neos>}, we want neos and add the day for each one.
    df = pd.DataFrame.from_records(
        [neo for _, neo_set in neo_data.items() for neo in neo_set]
    )
    # We want to know the specific date the neo is closest to the earth
    df["close_approach_date_full"] = df["close_approach_data"].apply(
        lambda approach_set: ",".join(
            approach["close_approach_date_full"] for approach in approach_set
        )
    )
    df["close_approach_date_full"] = pd.to_datetime(
        df["close_approach_date_full"], format="mixed"
    )

    df["relative_velocity_km_per_hour"] = df["close_approach_data"].apply(
        lambda approach_set: ",".join(
            approach["relative_velocity"]["kilometers_per_hour"]
            for approach in approach_set
        )
    )
    df["relative_velocity_km_per_hour"] = pd.to_numeric(
        df["relative_velocity_km_per_hour"]
    )

    df["miss_distance_km"] = df["close_approach_data"].apply(
        lambda approach_set: ",".join(
            approach["miss_distance"]["kilometers"] for approach in approach_set
        )
    )
    df["miss_distance_km"] = pd.to_numeric(df["miss_distance_km"])

    df["orbiting_body"] = df["close_approach_data"].apply(
        lambda approach_set: ",".join(
            approach["orbiting_body"] for approach in approach_set
        )
    )

    # We want to remove some columns
    df = df.drop(columns=["links", "close_approach_data", "sentry_data"])

    # Finally let's sort
    df = df.set_index("neo_reference_id")
    df = df.sort_values(by=["close_approach_date_full"])

    return df


@st.cache_data
def load_neo_by_id(neo_id):
    neo_data = get_neo_by_id(neo_id)
    return {key: value for key, value in neo_data.items() if key not in ("links", "id")}


def configure_page() -> None:
    st.set_page_config(page_title="Near Earth Object (NEO)", layout="wide")
    if "is_sentry_object" not in st.session_state:
        st.session_state.is_sentry_object = None
    if "is_potential_dangerous" not in st.session_state:
        st.session_state.is_potential_dangerous = None
    # if "neo_reference_id" not in st.session_state:
    #     st.session_state.neo_reference_id = None


def configure_overview() -> None:

    st.title("Near Earth Object (NEO) in the last 7 Days")


def configure_sidebar():
    st.session_state.is_sentry_object = st.sidebar.checkbox("Sentry Object")
    st.session_state.is_potential_dangerous = st.sidebar.checkbox(
        "Potential Dangerous Asteroid"
    )


def configure_selected_neo(event):
    rows = event.rows
    if rows:
        print(rows, rows[0], type(rows[0]))
        st.session_state.selected_neo = rows[0]


def show_data():
    raw_data = load_neo()
    if st.session_state.is_potential_dangerous is True:
        raw_data = raw_data[
            raw_data["is_potentially_hazardous_asteroid"]
            == st.session_state.is_potential_dangerous
        ]
    if st.session_state.is_sentry_object is True:
        raw_data = raw_data[
            raw_data["is_sentry_object"] == st.session_state.is_sentry_object
        ]
    data = raw_data.style.format(
        thousands=" ",
        decimal=",",
        precision=2,
    )

    st.dataframe(
        data,
        hide_index=True,
        column_order=[
            "close_approach_date_full",
            "name",
            "relative_velocity_km_per_hour",
            "miss_distance_km",
            "is_potentially_hazardous_asteroid",
            "is_sentry_object",
        ],
        key="neo_reference_id",
        column_config={
            "close_approach_date_full": "Closest Date",
            "name": "Name",
            "relative_velocity_km_per_hour": "Relative velocity (km/h)",
            "miss_distance_km": "Miss distance (km/h)",
            "is_potentially_hazardous_asteroid": "Potential Dangerous",
            "is_sentry_object": "Sentry Object",
        },
        on_select="rerun",
        selection_mode="single-row",
    )
    show_detail(raw_data)


def show_detail(data):
    if st.session_state.neo_reference_id is not None:
        # st.write(st.session_state.neo_reference_id)
        selected_rows = st.session_state.neo_reference_id.selection.rows
        if selected_rows:
            row = data.iloc[selected_rows[0]]
            neo_data = load_neo_by_id(row["id"])
            st.write(neo_data)


def main() -> None:
    configure_page()
    configure_overview()
    configure_sidebar()
    show_data()


if __name__ == "__main__":
    main()
