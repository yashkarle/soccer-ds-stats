#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Read in the match information files
"""
import pandas as pd
df = pd.read_csv('../Data/PL_2020-21_Player_Info.csv')
player_dict = df[['PlayerId', 'PlayerName']].drop_duplicates().set_index('PlayerId').to_dict()['PlayerName']

print(df)
print(player_dict[465527])