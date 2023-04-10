import streamlit as st
from st_row_buttons import st_row_buttons

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

    # Check if position is selected
    # if len(_selected_position_id) == 0:
    #     st.info("At least one position needs to be selected!")
    #     st.stop()

    return _competitions, _selected_competition_id, _positions, _selected_position_id


def _add_weighted_metric(_df, new_metric_name, weights):
    _df[new_metric_name] = 0.0
    weights_sum = 0.0
    for metric in weights:
        _df[new_metric_name] += _df[metric] * weights[metric]
        weights_sum += weights[metric]
    if weights_sum != 1:
        print("Warning while creating {}: weights do not add up to 1".format(new_metric_name))
    return _df


def _get_user_input_weights(final_metrics):
    overall_user_weights = dict()
    default_weight = 1.0/len(final_metrics)
    weights_sum = 0.0
    for metric in final_metrics:
        weight = st.number_input(
            label=metric,
            min_value=0.0,
            max_value=1.0,
            value=default_weight,
            step=0.05
        )
        weights_sum += weight
        overall_user_weights[metric] = weight
    if weights_sum != 1:
        st.write("WARNING: Weights do not add up to 1!")
    return overall_user_weights


def get_players_season_rankings(competitions, selected_competition_id, positions, selected_position_id):

    # Create Dataframe
    ret_df = twelve.get_season_players_ratings(competitions, selected_competition_id, positions, selected_position_id)

    base_cols = [
        'Player',
        'Team',
        'Position',
        'Foot',
        'Height',
        'Age',
        # 'Market value',
        # 'Contract expires',
        'Matches played',
        'Minutes played',
    ]

    raw_metrics = [col for col in ret_df.columns if col not in base_cols]
    ret_df = ret_df.dropna(subset=raw_metrics)
    for col in raw_metrics:
        ret_df['{col} prank'.format(col=col)] = ret_df[col].rank(pct=True)

    # Ball winner
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
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Ball winner', weights={
        'Aggression': 0.35,
        'Competitiveness': 0.35,
        'Decisions(off the ball)': 0.1,
        'Positioning': 0.2,
    })

    # Deep lying playmaker
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
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Progressive runs', weights={
        'Progressive runs per 90 prank': 0.5,
        'Accelerations per 90 prank': 0.3,
        'Dribbles per 90 prank': 0.2,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Deep lying playmaker', weights={
        'Decisions(on the ball)': 0.25,
        'Passes through the lines': 0.3,
        'Progressive passing': 0.35,
        'Progressive runs': 0.1,
    })

    # Attacking playmaker
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

    # Runner
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Dribbles', weights={
        'Dribbles per 90 prank': 0.5,
        'Successful dribbles, % prank': 0.5,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Runner', weights={
        'Decisions(on the ball)': 0.2,
        'Dribbles': 0.325,
        'Progressive passing': 0.15,
        'Progressive runs': 0.325,
    })

    # Tempo
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Pass accuracy', weights={
        'Accurate progressive passes, % prank': 0.3,
        'Accurate forward passes, % prank': 0.25,
        'Accurate long passes, % prank': 0.25,
        'Accurate passes, % prank': 0.2,
    })
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Tempo', weights={
        'Composure': 0.1,
        'Decisions(on the ball)': 0.2,
        'Pass accuracy': 0.3,
        'Progressive passing': 0.2,
        'Quality touches on the ball': 0.2,
    })

    final_metrics = [
        'Ball winner',
        'Deep lying playmaker',
        'Attacking playmaker',
        'Runner',
        'Tempo',
    ]
    # print(ret_df[base_cols+final_metrics].head())

    # Overall
    overall_user_weights = _get_user_input_weights(final_metrics)
    ret_df = _add_weighted_metric(ret_df, new_metric_name='Overall', weights=overall_user_weights)

    df = ret_df[base_cols+final_metrics+['Overall']]
    return df


# Use default settings
create_default_configs()

# Sidebar menu for competition and position
competitions_, selected_competition_id_, positions_, selected_position_id_ = sidebar_select_competition_and_seasons()

# Get the data
selected_sub_nav = st_row_buttons(['Player Ranking', 'Team Rankings'])

if selected_sub_nav == 'Player Ranking':

    # SUBPAGE 1
    # Title of the page
    st.title("Players Ranking - {} {}".format(
        competitions_[selected_competition_id_],
        positions_[selected_position_id_])
    )

    df_players_rankings = get_players_season_rankings(
        competitions_, selected_competition_id_,
        positions_, selected_position_id_
    )

    # Sidebar filter minutes
    max_age = st.sidebar.slider(
        label="Age",
        min_value=df_players_rankings['Age'].min().item(),
        max_value=df_players_rankings['Age'].max().item(),
        value=29)
    minimal_minutes = st.sidebar.slider(
        label="Minutes",
        min_value=0,
        max_value=1000,
        value=500
    )

    # Sidebar filter position, all positions in dataset
    # selected_positions = st.sidebar.multiselect("Positions", df_players_rankings['Position'].unique(),
    #                                             df_players_rankings['Position'].unique())

    # Checkbox
    # if st.sidebar.checkbox('Aggregate seasons', False):
    #     # Aggregate data from different seasons
    #     df_players_rankings = df_players_rankings.groupby(['player_id', 'player',
    #                                                        'team_id', 'team', 'position']).sum().reset_index()

    # FILTER data
    df_players_rankings = df_players_rankings[df_players_rankings['Minutes played'] >= minimal_minutes]
    df_players_rankings = df_players_rankings[df_players_rankings['Age'] <= max_age]
    # df_players_rankings = df_players_rankings[df_players_rankings['Position'].isin(selected_positions)]

    # Show Dataframe
    st.dataframe(df_players_rankings)

else:

    # SUBPAGE 2
    st.title("Team Ranking")
