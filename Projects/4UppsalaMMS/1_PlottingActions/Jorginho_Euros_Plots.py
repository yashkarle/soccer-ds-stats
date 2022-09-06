#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 23:49:41 2022

@author: yashkarle
"""
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen

parser = Sbopen()

df_competitions = parser.competition()
df_matches = parser.match(competition_id=55, season_id=43)
# Italy matches:
#   [3788741, 3788754, 3788766, 3794685, 3795107, 3795220, 3795506]
#   [Turkey, Switzerland, Wales, Austria, Belgium, Spain, England]

df, related, freeze, tactics = parser.event(3795107)
passes = (
    df.loc[df["type_name"] == "Pass"]
    .loc[df["sub_type_name"] != "Throw-in"]
    .set_index("id")
)

# TODO: df["pass_direction"] =
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
    "x",
    "y",
]


# Jorginho name: "Jorge Luiz Frello Filho"
# Jorgingo player_id: 7024
mask_jorgi_back = (
    (df.type_name == "Pass")
    & (df.player_name == "Jorge Luiz Frello Filho")
    & (df.end_x < df.x)
    & (~df.outcome_id.isin([9, 75, 76]))
)
mask_jorgi_front = (
    (df.type_name == "Pass")
    & (df.player_name == "Jorge Luiz Frello Filho")
    & (df.end_x > df.x)
    & (df.pass_length <= 25)
    & (~df.outcome_id.isin([9, 75, 76]))
)
mask_jorgi_front_prog = (
    (df.type_name == "Pass")
    & (df.player_name == "Jorge Luiz Frello Filho")
    & (df.end_x > df.x)
    & (df.pass_length > 25)
    & (~df.outcome_id.isin([9, 75, 76]))
)

df_pass_back = df.loc[mask_jorgi_back, ["x", "y", "end_x", "end_y"]]
df_pass_front = df.loc[mask_jorgi_front, ["x", "y", "end_x", "end_y"]]
df_pass_front_prog = df.loc[mask_jorgi_front_prog, ["x", "y", "end_x", "end_y"]]

pitch = Pitch(line_color="black")
fig, ax = pitch.grid(
    grid_height=0.9,
    title_height=0.06,
    axis=False,
    endnote_height=0.04,
    title_space=0,
    endnote_space=0,
)
fig.suptitle("Jorginho against Belgium", fontsize=30)

# pitch.arrows(df_pass_front_prog.x, df_pass_front_prog.y,
# df_pass_front_prog.end_x, df_pass_front_prog.end_y,
# color = "green", ax=ax['pitch'])
pitch.scatter(
    df_pass_front_prog.x,
    df_pass_front_prog.y,
    alpha=0.2,
    s=250,
    color="green",
    ax=ax["pitch"],
)

# pitch.arrows(df_pass_front.x, df_pass_front.y, df_pass_front.end_x,
# df_pass_front.end_y, color = "blue", ax=ax['pitch'])
pitch.scatter(
    df_pass_front.x, df_pass_front.y, alpha=0.2, s=250, color="blue", ax=ax["pitch"]
)

# pitch.arrows(df_pass_back.x, df_pass_back.y, df_pass_back.end_x,
# df_pass_back.end_y, color = "red", ax=ax['pitch'])
pitch.scatter(
    df_pass_back.x, df_pass_back.y, alpha=0.2, s=250, color="red", ax=ax["pitch"]
)

plt.show()
