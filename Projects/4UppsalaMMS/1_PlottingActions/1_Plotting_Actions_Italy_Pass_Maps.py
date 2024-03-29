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
from mplsoccer import Pitch, Sbopen

parser = Sbopen()

df_competitions = parser.competition()
df_matches = parser.match(competition_id=55, season_id=43)
# Italy matches:
#   [3788741, 3788754, 3788766, 3794685, 3795107, 3795220, 3795506]
#   [Turkey, Switzerland, Wales, Austria, Belgium, Spain, England]

# df_turkey, _, _, _ = parser.event(3788741)
# df_switzerland, _, _, _ = parser.event(3788754)
# df_wales, _, _, _ = parser.event(3788766)
# df_austria, _, _, _ = parser.event(3794685)
df_belgium, _, _, _ = parser.event(3795107)
df_spain, _, _, _ = parser.event(3795220)
df_england, _, _, _ = parser.event(3795506)

# passes = (
#     df.loc[df["type_name"] == "Pass"]
#     .loc[df["sub_type_name"] != "Throw-in"]
#     .set_index("id")
# )

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
    # make df with successfull passes by England until the first substitution
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


# df_cluster1 = df_turkey_passes.append(df_wales_passes, ignore_index=True)
# df_cluster1 = df_cluster1.append(df_england_passes, ignore_index=True)
# df_cluster2 = df_switzerland_passes.append(df_austria_passes, ignore_index=True)
# df_cluster2 = df_cluster2.append(df_belgium_passes, ignore_index=True)
# df_cluster3 = df_spain_passes


df_cluster1["pass_angle_degrees"] = df_cluster1["pass_angle"].apply(
    lambda x: math.degrees(x)
)
df_cluster2["pass_angle_degrees"] = df_cluster2["pass_angle"].apply(
    lambda x: math.degrees(x)
)
df_cluster3["pass_angle_degrees"] = df_cluster3["pass_angle"].apply(
    lambda x: math.degrees(x)
)


df_cluster1["pass_angle_degrees"] = df_cluster1["pass_angle_degrees"].apply(
    lambda x: (-x) if (x < 0) else (360 - x)
)
df_cluster2["pass_angle_degrees"] = df_cluster2["pass_angle_degrees"].apply(
    lambda x: (-x) if (x < 0) else (360 - x)
)
df_cluster3["pass_angle_degrees"] = df_cluster3["pass_angle_degrees"].apply(
    lambda x: (-x) if (x < 0) else (360 - x)
)


df_cluster1["pass_angle_back_weighted"] = df_cluster1["pass_angle_degrees"].apply(
    lambda x: -math.cos(x)
)
df_cluster2["pass_angle_back_weighted"] = df_cluster2["pass_angle_degrees"].apply(
    lambda x: -math.cos(x)
)
df_cluster3["pass_angle_back_weighted"] = df_cluster3["pass_angle_degrees"].apply(
    lambda x: -math.cos(x)
)


df_cluster1["pass_angle_side_weighted"] = df_cluster1["pass_angle_degrees"].apply(
    lambda x: math.pow(math.sin(x), 2)
)
df_cluster2["pass_angle_side_weighted"] = df_cluster2["pass_angle_degrees"].apply(
    lambda x: math.pow(math.sin(x), 2)
)
df_cluster3["pass_angle_side_weighted"] = df_cluster3["pass_angle_degrees"].apply(
    lambda x: math.pow(math.sin(x), 2)
)


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
