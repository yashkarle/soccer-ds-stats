import streamlit as st
from st_row_buttons import st_row_buttons

import data.twelve_api as twelve
import pandas as pd
from settings import create_default_configs


def sidebar_select_competition_and_seasons():
    # Single selector for competition
    competitions = twelve.competitions()
    selected_competition_id = st.sidebar.selectbox("Competition", competitions, format_func=lambda x: competitions[x])

    # Multi-selector for seasons
    # seasons = twelve.seasons()
    # selected_season_ids = st.sidebar.multiselect("Seasons", seasons, seasons, format_func=lambda x: seasons[x])

    # Check if seasons are selected
    # if len(selected_season_ids) == 0:
    #     st.info("At least one season needs to be selected!")
    #     st.stop()

    return competitions, selected_competition_id \
        # seasons, selected_season_ids


def _add_weighted_metric(_df, new_metric_name, weights):
    _df[new_metric_name] = 0.0
    weights_sum = 0.0
    for metric in weights:
        _df[new_metric_name] += _df[metric] * weights[metric]
        weights_sum += weights[metric]
    if weights_sum != 1:
        print("Error: weights do not add up to 1")
    return _df


def get_players_season_rankings(competitions, selected_competition_id):

    # Create Dataframe
    ret_df = twelve.get_season_players_ratings(competitions, selected_competition_id)
    print(ret_df.head())

    base_cols = [
        'Player',
        'Team',
        'Position',
        'Age',
        'Market value',
        'Contract expires',
        'Matches played',
        'Minutes played',
        'Foot',
        'Height',
    ]

    for col in ret_df.columns:
        if col not in base_cols:
            ret_df['{col} prank'.format(col=col)] = ret_df[col].rank(pct=True)

    print(ret_df.head())

    ret_df = _add_weighted_metric(ret_df, new_metric_name='Aggression', weights={
        'Fouls per 90 prank': 0.3,
        'Sliding tackles per 90 prank': 0.1,
        'Defensive duels per 90 prank': 0.3,
        'Yellow cards per 90 prank': 0.3,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Competitiveness', weights={
        'Defensive duels per 90 prank': 0.5,
        'Sliding tackles per 90 prank': 0.2,
        'Shots blocked per 90 prank': 0.3,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Decisions(off the ball)', weights={
        'Received passes per 90 prank': 1,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Positioning', weights={
        'Shots blocked per 90 prank': 0.5,
        'Interceptions per 90 prank': 0.5,
    })
    # Ball winner
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Ball winner', weights={
        'Aggression': 0.35,
        'Competitiveness': 0.35,
        'Decisions(off the ball)': 0.1,
        'Positioning': 0.2,
    })

    ret_df = _add_weighted_metric(ret_df, new_metric_name='Decisions(on the ball)', weights={
        'Accurate passes to penalty area, % prank': 0.2,
        'Accurate progressive passes, % prank': 0.2,
        'Accurate through passes, % prank': 0.15,
        'Successful dribbles, % prank': 0.25,
        'Accurate long passes, % prank': 0.2,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Passes through the lines', weights={
        'Through passes per 90 prank': 0.5,
        'Accurate through passes, % prank': 0.5,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Progressive passing', weights={
        'Forward passes per 90 prank': 0.1,
        'Accurate forward passes, % prank': 0.1,
        'Long passes per 90 prank': 0.1,
        'Accurate long passes, % prank': 0.1,
        'Progressive passes per 90 prank': 0.2,
        'Accurate progressive passes, % prank': 0.2,
        'Deep completions per 90 prank': 0.2,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Progressive Runs', weights={
        'Progressive runs per 90 prank': 0.5,
        'Accelerations per 90 prank': 0.3,
        'Dribbles per 90 prank': 0.2,
    })
    # Deep lying playmaker
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Deep lying playmaker', weights={
        'Decisions(on the ball)': 0.25,
        'Passes through the lines': 0.3,
        'Progressive passing': 0.35,
        'Progressive Runs': 0.1,
    })

    ret_df = _add_weighted_metric(ret_df, new_metric_name='Composure', weights={
        'Deep completions per 90 prank': 0.5,
        'Shots on target, % prank': 0.5,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Goal contributions', weights={
        'xG per 90 prank': 0.2,
        'Non-penalty goals per 90 prank': 0.3,
        'Assists per 90 prank': 0.3,
        'xA per 90 prank': 0.2,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Pass delivery', weights={
        'Accurate forward passes, % prank': 0.3,
        'Accurate long passes, % prank': 0.2,
        'Accurate passes, % prank': 0.2,
        'Accurate progressive passes, % prank': 0.3,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Quality final action', weights={
        'Passes to penalty area per 90 prank': 0.1,
        'Accurate passes to penalty area, % prank': 0.2,
        'Shot assists per 90 prank': 0.15,
        'xA per 90 prank': 0.1,
        'Assists per 90 prank': 0.2,
        'Shots per 90 prank': 0.1,
        'Shots on target, % prank': 0.15,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Quality touches on the ball', weights={
        'Fouls suffered per 90 prank': 0.3,
        'Smart passes per 90 prank': 0.25,
        'Accurate smart passes, % prank': 0.25,
        'Key passes per 90 prank': 0.2,
    })
    # Attacking playmaker
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Attacking playmaker', weights={
        'Composure': 0.05,
        'Decisions(on the ball)': 0.1,
        'Goal contributions': 0.125,
        'Pass delivery': 0.2,
        'Passes through the lines': 0.175,
        'Progressive passing': 0.15,
        'Quality final action': 0.15,
        'Quality touches on the ball': 0.15,
    })

    runner_cols = [
        'Accelerations per 90 prank',
        'Progressive runs per 90 prank',
        'Dribbles per 90 prank',
        'Accurate progressive passes, % prank',
        'Progressive passes per 90 prank',
        'Deep completions per 90 prank',
        'Accurate long passes, % prank',
        'Long passes per 90 prank',
        'Accurate forward passes, % prank',
        'Forward passes per 90 prank',
        'Successful dribbles, % prank',
        'Dribbles per 90 prank',
        'Accurate through passes, % prank',
        'Accurate passes to penalty area, % prank'
    ]

    tempo_cols = [
        'Accurate smart passes, % prank',
        'Key passes per 90 prank',
        'Smart passes per 90 prank',
        'Fouls suffered per 90 prank',
        'Accurate progressive passes, % prank',
        'Progressive passes per 90 prank',
        'Deep completions per 90 prank',
        'Accurate long passes, % prank',
        'Long passes per 90 prank',
        'Accurate forward passes, % prank',
        'Forward passes per 90 prank',
        'Accurate passes, % prank',
        'Successful dribbles, % prank',
        'Accurate passes to penalty area, % prank',
        'Accurate through passes, % prank',
        'Shots on target, % prank'
    ]

    metrics_calc_cols = [
        # Runner
        'Decisions(on the ball)',
        'Dribbles',
        'Effective pressing',
        'Progressive passing',
        'Progressive runs',
        # Tempo
        'Composure',
        'Decisions(on the ball)',
        'Pass accuracy',
        'Progressive passing',
        'Quality touches on the ball',
    ]

    final_metrics = [
        'Ball winner',
        'Deep lying playmaker',
        'Attacking playmaker',
        # 'Runner',
        # 'Tempo',
    ]
    print(ret_df[final_metrics].head())

    df = ret_df[final_metrics]
    return df


# Use default settings
create_default_configs()

# Sidebar menu for competition and seasons
competitions, selected_competition_id = sidebar_select_competition_and_seasons()

# Get the data
selected_sub_nav = st_row_buttons(['Player Ranking', 'Team Rankings'])

if selected_sub_nav == 'Player Ranking':

    # SUBPAGE 1
    # Title of the page
    st.title("Players Ranking")

    df_players_rankings = get_players_season_rankings(competitions, selected_competition_id)

    # Sidebar filter minutes
    minimal_minutes = st.sidebar.slider("Minutes", 0, 1000, 500)

    # Sidebar filter position, all positions in dataset
    selected_positions = st.sidebar.multiselect("Positions", df_players_rankings['Position'].unique(),
                                                df_players_rankings['Position'].unique())

    # Checkbox
    # if st.sidebar.checkbox('Aggregate seasons', False):
    #     # Aggregate data from different seasons
    #     df_players_rankings = df_players_rankings.groupby(['player_id', 'player',
    #                                                        'team_id', 'team', 'position']).sum().reset_index()

    # FILTER data
    df_players_rankings = df_players_rankings[df_players_rankings['Minutes played'] >= minimal_minutes]
    df_players_rankings = df_players_rankings[df_players_rankings['Position'].isin(selected_positions)]

    # Show Dataframe
    st.dataframe(df_players_rankings)

else:

    # SUBPAGE 2
    st.title("Team Ranking")
