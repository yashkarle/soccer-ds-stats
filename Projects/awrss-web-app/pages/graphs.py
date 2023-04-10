import streamlit as st
from st_row_buttons import st_row_buttons
import plotly.express as px

import data.twelve_api as twelve
from settings import create_default_configs


def sidebar_select_competition_and_seasons():
    # Single selector for competition
    _competitions = twelve.get_competitions()
    _selected_competition_id = st.sidebar.selectbox(
        "Competition", _competitions, format_func=lambda x: _competitions[x]
    )

    # Single selector for seasons
    _positions = twelve.get_positions()
    _selected_position_id = st.sidebar.selectbox(
        "Position", _positions, format_func=lambda x: _positions[x]
    )

    return _competitions, _selected_competition_id, _positions, _selected_position_id


def get_players_season_data(competitions, selected_competition_id, positions, selected_position_id):

    # Create Dataframe
    ret_df = twelve.get_season_players_ratings(competitions, selected_competition_id, positions, selected_position_id)

    base_cols = [
        'Player',
        'Team',
        'Position',
        'Foot',
        'Height',
        'Age',
        'Matches played',
        'Minutes played',
        'Market value',
        'Contract expires',
    ]

    raw_metrics = [col for col in ret_df.columns if col not in base_cols]
    ret_df = ret_df.dropna(subset=raw_metrics)
    calc_metrics_dict = dict()
    calc_metric_idx = 1
    for col in raw_metrics:
        ret_df['{col} prank'.format(col=col)] = ret_df[col].rank(pct=True)
        calc_metrics_dict[calc_metric_idx] = '{col} prank'.format(col=col)
        calc_metric_idx += 1

    return ret_df, calc_metrics_dict


# Use default settings
create_default_configs()

# Sidebar menu for competition and position
competitions_, selected_competition_id_, positions_, selected_position_id_ = sidebar_select_competition_and_seasons()

# Get the data
selected_sub_nav = st_row_buttons(['Player Graphs', 'Team Graphs'])

if selected_sub_nav == 'Player Graphs':

    # SUBPAGE 1
    # Title of the page
    st.title("Players Graphs - {} {}".format(
        competitions_[selected_competition_id_],
        positions_[selected_position_id_])
    )

    df_players, calc_metrics = get_players_season_data(
        competitions_, selected_competition_id_,
        positions_, selected_position_id_
    )

    # Single selector for metric X
    _selected_metric_x_idx = st.selectbox(
        "Metric X", calc_metrics.keys(), format_func=lambda x: calc_metrics[x]
    )
    # Single selector for metric Y
    _selected_metric_y_idx = st.selectbox(
        "Metric Y", calc_metrics.keys(), format_func=lambda x: calc_metrics[x]
    )

    # Sidebar filter minutes
    max_age = st.sidebar.slider(
        label="Age",
        min_value=df_players['Age'].min().item(),
        max_value=df_players['Age'].max().item(),
        value=29)
    minimal_minutes = st.sidebar.slider(
        label="Minutes",
        min_value=0,
        max_value=1000,
        value=500
    )

    # FILTER data
    df_players = df_players[df_players['Minutes played'] >= minimal_minutes]
    df_players = df_players[df_players['Age'] <= max_age]

    fig = px.scatter(
        df_players,
        x=calc_metrics[_selected_metric_x_idx],
        y=calc_metrics[_selected_metric_y_idx],
        size="Minutes played",
        color="Team",
        hover_name="Player",
        # log_x=True,
        # size_max=60,
    )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

else:

    # SUBPAGE 2
    st.title("Team Ranking")
