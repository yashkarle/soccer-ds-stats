import json
import matplotlib.pyplot as plt

from football_viz import plot_pitch_skc, plot_ff
from helper import transform_to_sck
from settings import DATA_FOLDER_FF, prefix

"""
    Example of reading freeze frame file and plot
"""
if __name__ == '__main__':

    # Random Match
    match_id = '2128288'

    # Read Data
    with open(f"{DATA_FOLDER_FF}/{match_id}{prefix}", 'r') as in_file:
        freeze_frame = json.load(in_file)

    # Select Frame
    selected_ff = freeze_frame[19] # Random Selection

    fig, ax = plot_pitch_skc(field_color='w', figsize=(10, 7))

    # Plot All the players
    plot_ff(selected_ff['adjusted_data'], ax)

    # Plot Ball Location if available
    if 'ball_loc_x_opta' in selected_ff:
        b_loc = transform_to_sck(selected_ff['ball_loc_x_opta'], selected_ff['ball_loc_y_opta'])
        ax.plot(b_loc[0],
                b_loc[1],
                '*',
                color='k',
                MarkerSize=12,
                alpha=1.0,
                zorder=5
                )

    plt.show()