#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 23:49:41 2022

@author: yashkarle
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
from mplsoccer import Sbopen, Pitch, FontManager

parser = Sbopen()

df_competitions = parser.competition()
df_matches = parser.match(competition_id=55, season_id=43)
# Italy matches:
#   [3788741, 3788754, 3788766, 3794685, 3795107, 3795220, 3795506]
#   [Turkey, Switzerland, Wales, Austria, Belgium, Spain, England]

df_belgium, _, _, _ = parser.event(3795107)
df_spain, _, _, _ = parser.event(3795220)
df_england, _, _, _ = parser.event(3795506)

useful_cols = [
    "counterpress",
    "duration",
    "end_x",
    "end_y",
    "id",
    "index",
    "match_id",
    "minute",
    "outcome_id",
    "outcome_name",
    "pass_angle",
    "pass_assisted_shot_id",
    "pass_goal_assist",
    "pass_length",
    "pass_recipient_id",
    "pass_recipient_name",
    "pass_shot_assist",
    "period",
    "player_id",
    "player_name",
    "position_id",
    "position_name",
    "possession",
    "possession_team_id",
    "possession_team_name",
    "second",
    "shot_key_pass_id",
    "shot_statsbomb_xg",
    "team_id",
    "team_name",
    "timestamp",
    "type_name",
    "x",
    "y",
]


def mask_team_passes(df, team_name, cols):
    # check for index of first sub
    sub = (
        df.loc[df["type_name"] == "Substitution"]
        .loc[df["team_name"] == team_name]
        .iloc[0]["index"]
    )
    # make df with successfull passes by the team until the first substitution
    mask = (
        (df.type_name == "Pass")
        & (df.team_name == team_name)
        & (df.index < sub)
        & (df.outcome_name.isnull())
        & (df.sub_type_name != "Throw-in")
    )
    # taking necessary columns
    df_pass = df.loc[mask, cols]
    # adjusting that only the surname of a player is presented.
    df_pass["player_name"] = df_pass["player_name"].apply(lambda x: str(x).split()[-1])
    df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].apply(
        lambda x: str(x).split()[-1]
    )

    return df_pass


df_belgium_passes = mask_team_passes(df_belgium, team_name="Italy", cols=useful_cols)
df_spain_passes = mask_team_passes(df_spain, team_name="Italy", cols=useful_cols)
df_england_passes = mask_team_passes(df_england, team_name="Italy", cols=useful_cols)


# calculate number of successful passes by player
def print_centralisation_index(df_pass):
    no_passes = df_pass.groupby(["player_name"]).x.count().reset_index()
    no_passes.rename({"x": "pass_count"}, axis="columns", inplace=True)

    # find one who made most passes
    max_no = no_passes["pass_count"].max()
    # calculate the denominator - 10*the total sum of passes
    denominator = 10 * no_passes["pass_count"].sum()
    # calculate the nominator
    nominator = (max_no - no_passes["pass_count"]).sum()
    # calculate the centralisation index
    centralisation_index = nominator / denominator

    print("Centralisation index is ", centralisation_index)


print_centralisation_index(df_belgium_passes)
print_centralisation_index(df_spain_passes)
print_centralisation_index(df_england_passes)


def get_pass_orientation_weights(df_pass):
    df_pass["pass_angle_degrees"] = df_pass["pass_angle"].apply(
        lambda x: math.degrees(x)
    )
    df_pass["pass_angle_degrees"] = df_pass["pass_angle_degrees"].apply(
        lambda x: (-x) if (x < 0) else (360 - x)
    )
    df_pass["pass_angle_back_weighted"] = df_pass["pass_angle_degrees"].apply(
        lambda x: -math.cos(x)
    )
    df_pass["pass_angle_side_weighted"] = df_pass["pass_angle_degrees"].apply(
        lambda x: math.pow(math.sin(x), 2)
    )

    return df_pass


df_belgium_passes = get_pass_orientation_weights(df_belgium_passes)
df_spain_passes = get_pass_orientation_weights(df_spain_passes)
df_england_passes = get_pass_orientation_weights(df_england_passes)


def calc_node_size_and_loc(df_pass):
    scatter_df = pd.DataFrame()

    for i, name in enumerate(df_pass["player_name"].unique()):
        passx = df_pass.loc[df_pass["player_name"] == name]["x"].to_numpy()
        recx = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
        passy = df_pass.loc[df_pass["player_name"] == name]["y"].to_numpy()
        recy = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_y"].to_numpy()

        # make sure that x and y location for each circle representing the player
        # is the average of passes and receptions
        scatter_df.at[i, "player_name"] = name
        scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
        scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))

        # calculate number of passes
        scatter_df.at[i, "no"] = (
            df_pass.loc[df_pass["player_name"] == name].count().loc["id"]
        )

    # adjust the size of a circle so that the player who made more passes
    scatter_df["marker_size"] = scatter_df["no"] / scatter_df["no"].max() * 1500

    return scatter_df


df_belgium_nodes = calc_node_size_and_loc(df_belgium_passes)
df_spain_nodes = calc_node_size_and_loc(df_spain_passes)
df_england_nodes = calc_node_size_and_loc(df_england_passes)


def calc_edge_width(df_pass, minutes_till_first_sub, pass_weighting, pass_threshold):
    # counting passes between players
    df_pass["pair_key"] = df_pass.apply(
        lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1
    )

    if pass_weighting == "back":
        weight_col = "pass_angle_back_weighted"
    elif pass_weighting == "side":
        weight_col = "pass_angle_side_weighted"
    lines_df = (
        df_pass.groupby(["pair_key"])
        .agg({"x": ["count"], weight_col: ["mean"]})
        .reset_index()
    )
    lines_df.columns = ["pair_key", "pass_count", "pass_weight"]
    lines_df["pass_count"] = lines_df["pass_count"] * 90 / minutes_till_first_sub

    # setting a treshold. You can try to investigate how it changes when you change it.
    lines_df = lines_df[lines_df["pass_count"] > pass_threshold]

    return lines_df


df_belgium_edges = calc_edge_width(
    df_belgium_passes,
    minutes_till_first_sub=74,
    pass_weighting="back",
    pass_threshold=3,
)
df_spain_edges = calc_edge_width(
    df_spain_passes, minutes_till_first_sub=61, pass_weighting="back", pass_threshold=2
)
df_england_edges = calc_edge_width(
    df_england_passes,
    minutes_till_first_sub=54,
    pass_weighting="back",
    pass_threshold=5,
)


def plot_pass_nw_grid(
    df_belgium_nodes,
    df_belgium_edges,
    df_spain_nodes,
    df_spain_edges,
    # df_england_nodes,
    # df_england_edges,
    opposition_names,
):
    # plot the pitch and vertices
    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#22312b",
        line_color="#c7d5cc",
        pad_top=(10),
    )
    fig, axs = pitch.grid(
        ncols=2,
        nrows=1,
        grid_height=0.82,
        title_height=0.08,
        axis=False,
        endnote_height=0.05,
        title_space=0,
        endnote_space=0,
        figheight=7,
    )
    fig.set_facecolor("#22312b")

    # Load a custom font.
    # URL = "https://github.com/google/fonts/blob/main/apache/roboto/Roboto%5Bwdth,wght%5D.ttf?raw=true"
    # robotto_regular = FontManager(URL)

    # for each opponent
    for team_name, ax in zip(
        opposition_names, axs["pitch"].flat[: len(opposition_names)]
    ):
        # put player name over the plot
        ax.text(
            60,
            -10,
            "vs " + team_name,
            ha="center",
            va="center",
            fontsize=18,
            # fontproperties=robotto_regular.prop,
            color="#c7d5cc",
        )

        if team_name == "Belgium":
            scatter_df = df_belgium_nodes
            lines_df = df_belgium_edges
        elif team_name == "Spain":
            scatter_df = df_spain_nodes
            lines_df = df_spain_edges
        # elif team_name == "England":
        # scatter_df = df_england_nodes
        # lines_df = df_england_edges

        pitch.scatter(
            scatter_df.x,
            scatter_df.y,
            s=500,
            color="blue",
            edgecolors="black",
            linewidth=1,
            alpha=1,
            ax=ax,
            zorder=3,
        )
        for i, row in scatter_df.iterrows():
            if row.player_name == "Filho":
                row.player_name = "Jorginho"
            elif row.player_name == "Santos":
                row.player_name = "Emerson"

            player_name_jersey_number_map = {
                "Donnarumma": "21",
                "Lorenzo": "2",
                "Bonucci": "19",
                "Chiellini": "3",
                "Spinazzola": "4",
                "Emerson": "13",
                "Jorginho": "8",
                "Verratti": "6",
                "Barella": "18",
                "Chiesa": "14",
                "Insigne": "10",
                "Immobile": "17",
            }

            pitch.annotate(
                player_name_jersey_number_map[row.player_name],
                xy=(row.x, row.y),
                color="white",
                va="center",
                ha="center",
                weight="bold",
                size=12,
                ax=ax,
                zorder=4,
            )

        for i, row in lines_df.iterrows():
            player1 = row["pair_key"].split("_")[0]
            player2 = row["pair_key"].split("_")[1]
            # take the average location of players to plot a line between them
            player1_x = scatter_df.loc[scatter_df["player_name"] == player1]["x"].iloc[
                0
            ]
            player1_y = scatter_df.loc[scatter_df["player_name"] == player1]["y"].iloc[
                0
            ]
            player2_x = scatter_df.loc[scatter_df["player_name"] == player2]["x"].iloc[
                0
            ]
            player2_y = scatter_df.loc[scatter_df["player_name"] == player2]["y"].iloc[
                0
            ]
            num_passes = row["pass_count"]
            pass_weight = row["pass_weight"]
            # adjust the line width so that the more passes, the wider the line
            line_width = num_passes * pass_weight / lines_df["pass_count"].max() * 18
            # plot lines on the pitch
            pitch.lines(
                player1_x,
                player1_y,
                player2_x,
                player2_y,
                alpha=1,
                lw=line_width,
                zorder=2,
                color="white",
                ax=ax,
            )

    # endnote /title
    axs["endnote"].text(
        1,
        0.5,
        "*passes weighted to highlight back passes and normalized to reflect per 90 minutes values",
        color="#c7d5cc",
        va="center",
        ha="right",
        fontsize=16,
        # fontproperties=robotto_regular.prop,
    )
    TITLE_TEXT = "Italy passing network (EURO 2020)"
    axs["title"].text(
        0.5,
        0.7,
        TITLE_TEXT,
        color="#c7d5cc",
        va="center",
        ha="center",
        # fontproperties=robotto_regular.prop,
        fontsize=20,
    )

    plt.show()


plot_pass_nw_grid(
    df_belgium_nodes,
    df_belgium_edges,
    df_spain_nodes,
    df_spain_edges,
    # df_england_nodes,
    # df_england_edges,
    opposition_names=["Belgium", "Spain"],
)
