import streamlit as st
from st_row_buttons import st_row_buttons

import data.twelve_api as twelve
import pandas as pd
from settings import create_default_configs

#
#    UI
#


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
#
#    DATA PROCESSOR
#


def get_players_season_rankings(competitions, selected_competition_id):

    # Create Dataframe
    data = list()
    ret_df = twelve.get_season_players_ratings(competitions, selected_competition_id)
    # for k in ret.keys():  # Seasons
    #
    #     season_rankings = ret[k]
    #     for row in ret_df:
    #         # print()
    #         data.append({
    #             'player_id': row['playerId'],
    #             'player': row['playerName'],
    #             'team_id': row['teamId'],
    #             'team': row['teamName'],
    #             'position': 'other' if  row['position'] is None else row['position'],
    #             'points': row['totalLeaguePoint']/1000,
    #             'attack': next((x for x in row['points'] if x['type'] == 'attack'), {'value': 0})['value'],
    #             'defence': next((x for x in row['points'] if x['type'] == 'defence'), {'value': 0})['value'],
    #             'shot':  next((x for x in row['points'] if x['type'] == 'shot'), {'value': 0})['value'],
    #             'matches': row['matchesCount'],
    #             'minutes': row['playedMin'],
    #             # 'season': k,
    #             # TODO: can add other attributes if needed
    #         })

    # df = pd.DataFrame(data)
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
