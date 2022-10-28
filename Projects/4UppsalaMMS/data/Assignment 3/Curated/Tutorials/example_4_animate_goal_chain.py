import pandas as pd
import json
import matplotlib.pyplot as plt

from football_viz import plot_pitch_skc, plot_ff
from helper import transform_to_sck
from settings import PROCESSED_FOLDER, df_output_name, pattern_match, ff_output_name



# Read Previous Processed data (Example 2)
if not('event_data' in locals()):
    event_data = pd.read_csv(f"{PROCESSED_FOLDER}{df_output_name}.csv")

    # Create Id - to match it Freeze Frames
    event_data['id'] = event_data[['match_id', 'event_id']].apply(lambda x: pattern_match.format(x['match_id'], x['event_id']),axis=1)

    # Read Processed Freeze Frames
    with open(f"{PROCESSED_FOLDER}/{ff_output_name}.json", 'r') as f:
        ff_dict = json.load(f)

# Find Possession Chain With Goal
selected_chain = event_data[event_data['goal'] == 1].iloc[13]
selected = event_data[(event_data['chain_id'] == selected_chain['chain_id']) & (event_data['match_id']== selected_chain['match_id'])]


# fig, axe = plt.subplots(nrows=len(selected), ncols=1, figsize=(5, len(selected)*1))
# axes = axe.flatten()

# Visualize all events Leading to goal
index = 0
for idx, event in selected.iterrows():

    # Get Opta Event
    start_x = event['x']
    start_y = event['y']
    end_x = event['x2']
    end_y = event['y2']

    # Get Freeze Frame if Exists
    ff = ff_dict.get(event['id'], None)

    # Pitch
    fig, ax = plot_pitch_skc(field_color='w',figsize=(10, 7))

    # Plot Freeze Frame
    if ff is not None:
        plot_ff(ff, ax)

    # Arrow - Pass
    start_loc = transform_to_sck(start_x, start_y)

    if end_x == end_x: # Not None
        end_loc = transform_to_sck(end_x, end_y)
        ax.annotate('', xytext=(start_loc[0], start_loc[1]), ha='center', va='center', xy=(end_loc[0], end_loc[1]), arrowprops=dict(arrowstyle="->", color='k'), size=30, zorder=5)

    # Plot Ball
    # Plot Ball Location if available
    b_loc = transform_to_sck(start_x, start_y)
    ax.plot(b_loc[0],
            b_loc[1],
            'o',
            color='k',
            markersize=12,
            alpha=1.0,
            zorder=5
            )
    index +=1

plt.show()