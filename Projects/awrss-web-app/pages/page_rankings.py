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
    for metric in weights:
        _df[new_metric_name] += _df[metric] * weights[metric]
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

    aggression_weights = {
        'Fouls per 90 prank': 0.3,
        'Sliding tackles per 90 prank': 0.1,
        'Defensive duels per 90 prank': 0.3,
        'Yellow cards per 90 prank': 0.3,
    }
    ret_df = _add_weighted_metric(ret_df, 'Aggression', aggression_weights)

    competitiveness_weights = {
        'Defensive duels per 90 prank': 0.5,
        'Sliding tackles per 90 prank': 0.2,
        'Shots blocked per 90 prank': 0.3,
    }
    ret_df = _add_weighted_metric(ret_df, 'Competitiveness', competitiveness_weights)

    decisions_off_ball_weights = {
        'Received passes per 90 prank': 1,
    }
    ret_df = _add_weighted_metric(ret_df, 'Decisions(off the ball)', decisions_off_ball_weights)

    positioning_weights = {
        'Shots blocked per 90 prank': 0.5,
        'Interceptions per 90 prank': 0.5,
    }
    ret_df = _add_weighted_metric(ret_df, 'Positioning', positioning_weights)
    ball_winner_weights = {
        'Aggression': 0.35,
        'Competitiveness': 0.35,
        'Decisions(off the ball)': 0.1,
        'Positioning': 0.2
    }
    ret_df = _add_weighted_metric(ret_df, 'Ball winner', ball_winner_weights)

    print(ret_df.head())

    deep_play_cols = [
        'Successful dribbles, %',
        'Accurate passes to penalty area, %',
        'Accurate through passes, %',
        'Accurate progressive passes, %',
        'Through passes per 90',
        'Forward passes per 90',
        'Accurate forward passes, %',
        'Long passes per 90',
        'Accurate long passes, %',
        'Deep completions per 90',
        'Progressive passes per 90',
        'Dribbles per 90',
        'Progressive runs per 90',
        'Accelerations per 90',
    ]

    att_play_cols = [
        'Shots on target, %',
        'Deep completions per 90',
        'Successful dribbles, %',
        'Accurate long passes, %',
        'Accurate passes to penalty area, %',
        'Accurate through passes, %',
        'Accurate progressive passes, %',
        'Non-penalty goals per 90',
        'xG per 90',
        'Assists per 90',
        'xA per 90',
        'Accurate passes, %',
        'Accurate forward passes, %',
        'Through passes per 90',
        'Accurate through passes, %',
        'Forward passes per 90',
        'Long passes per 90',
        'Progressive passes per 90'
        'Passes to penalty area per 90',
        'Shot assists per 90',
        'Shots per 90',
        'Shots on target, %',
        'Fouls suffered per 90',
        'Smart passes per 90',
        'Accurate smart passes, %',
        'Key passes per 90',
    ]

    runner_cols = [
        'Accelerations per 90',
        'Progressive runs per 90',
        'Dribbles per 90',
        'Accurate progressive passes, %',
        'Progressive passes per 90',
        'Deep completions per 90',
        'Accurate long passes, %',
        'Long passes per 90',
        'Accurate forward passes, %',
        'Forward passes per 90',
        'Successful dribbles, %',
        'Dribbles per 90',
        'Accurate through passes, %',
        'Accurate passes to penalty area, %'
    ]

    tempo_cols = [
        'Accurate smart passes, %',
        'Key passes per 90',
        'Smart passes per 90',
        'Fouls suffered per 90',
        'Accurate progressive passes, %',
        'Progressive passes per 90',
        'Deep completions per 90',
        'Accurate long passes, %',
        'Long passes per 90',
        'Accurate forward passes, %',
        'Forward passes per 90',
        'Accurate passes, %',
        'Successful dribbles, %',
        'Accurate passes to penalty area, %',
        'Accurate through passes, %',
        'Shots on target, %'
    ]

    metrics_calc_cols = [
        # Ball winner
        'Aggression',
        'Competitiveness',
        'Decisions(off the ball)',
        'Positioning',
        # Deep lying playmaker
        'Decisions(on the ball)',
        'Passes through the lines',
        'Progressive passing',
        'Progressive Runs',
        # Attacking playmaker
        'Composure',
        'Decisions(on the ball)',
        'Goal contributions',
        'Pass delivery',
        'Passes through the lines',
        'Progressive passing',
        'Quality final action',
        'Quality touches on the ball',
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
        'Runner',
        'Tempo',
    ]

    df = ret_df
    return df.assign(attack_p90=df['Progressive runs per 90'])\
        .assign(defence_p90=df['Interceptions per 90'])\
        .assign(shot_p90=df['Shots per 90'])


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
