import matplotlib.pyplot as plt
import numpy as np

from helper import transform_to_sck

"""

@author: Laurie Shaw (@EightyFivePoint)

@modified : Jernej Fliasr @flijer

"""


def plot_pitch_skc(figax=None, field_dimen=(105.0, 68.0), field_color='green', linewidth=2, markersize=20, figsize=(13,10)):
    """ plot_pitch

    Plots a soccer pitch. All distance units converted to meters.

    Parameters
    -----------
        field_dimen: (length, width) of field in meters. Default is (105,68)
        field_color: color of field. options are {'green','white'}
        linewidth  : width of lines. default = 2
        markersize : size of markers (e.g. penalty spot, centre spot, posts). default = 20

    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)

    """
    if figax is None:
        fig, ax = plt.subplots(figsize=figsize) # create a figure
    else:
        fig, ax = figax

    # decide what color we want the field to be. Default is green, but can also choose white
    if field_color == 'green':
        ax.set_facecolor('mediumseagreen')
        lc = 'whitesmoke'  # line color
        pc = 'w'  # 'spot' colors
    else:
        ax.set_facecolor(field_color)
        lc = 'grey'
        pc = 'k'
    # ALL DIMENSIONS IN m
    border_dimen = (3, 3)  # include a border arround of the field of width 3m
    meters_per_yard = 0.9144  # unit conversion from yards to meters
    half_pitch_length = field_dimen[0] / 2.  # length of half pitch
    half_pitch_width = field_dimen[1] / 2.  # width of half pitch
    signs = [-1, 1]
    # Soccer field dimensions typically defined in yards, so we need to convert to meters
    goal_line_width = 8 * meters_per_yard
    box_width = 20 * meters_per_yard
    box_length = 6 * meters_per_yard
    area_width = 44 * meters_per_yard
    area_length = 18 * meters_per_yard
    penalty_spot = 12 * meters_per_yard
    corner_radius = 1 * meters_per_yard
    D_length = 8 * meters_per_yard
    D_radius = 10 * meters_per_yard
    D_pos = 12 * meters_per_yard
    centre_circle_radius = 10 * meters_per_yard
    # plot half way line # center circle
    ax.plot([0, 0], [-half_pitch_width, half_pitch_width], lc, linewidth=linewidth)
    ax.scatter(0.0, 0.0, marker='o', facecolor=lc, linewidth=0, s=markersize)
    y = np.linspace(-1, 1, 50) * centre_circle_radius
    x = np.sqrt(centre_circle_radius ** 2 - y ** 2)
    ax.plot(x, y, lc, linewidth=linewidth)
    ax.plot(-x, y, lc, linewidth=linewidth)
    for s in signs:  # plots each line seperately
        # plot pitch boundary
        ax.plot([-half_pitch_length, half_pitch_length], [s * half_pitch_width, s * half_pitch_width], lc,
                linewidth=linewidth)
        ax.plot([s * half_pitch_length, s * half_pitch_length], [-half_pitch_width, half_pitch_width], lc,
                linewidth=linewidth)
        # goal posts & line
        ax.plot([s * half_pitch_length, s * half_pitch_length], [-goal_line_width / 2., goal_line_width / 2.], pc + 's',
                markersize=6 * markersize / 20., linewidth=linewidth)
        # 6 yard box
        ax.plot([s * half_pitch_length, s * half_pitch_length - s * box_length], [box_width / 2., box_width / 2.], lc,
                linewidth=linewidth)
        ax.plot([s * half_pitch_length, s * half_pitch_length - s * box_length], [-box_width / 2., -box_width / 2.], lc,
                linewidth=linewidth)
        ax.plot([s * half_pitch_length - s * box_length, s * half_pitch_length - s * box_length],
                [-box_width / 2., box_width / 2.], lc, linewidth=linewidth)
        # penalty area
        ax.plot([s * half_pitch_length, s * half_pitch_length - s * area_length], [area_width / 2., area_width / 2.],
                lc, linewidth=linewidth)
        ax.plot([s * half_pitch_length, s * half_pitch_length - s * area_length], [-area_width / 2., -area_width / 2.],
                lc, linewidth=linewidth)
        ax.plot([s * half_pitch_length - s * area_length, s * half_pitch_length - s * area_length],
                [-area_width / 2., area_width / 2.], lc, linewidth=linewidth)
        # penalty spot
        ax.scatter(s * half_pitch_length - s * penalty_spot, 0.0, marker='o', facecolor=lc, linewidth=0, s=markersize)
        # corner flags
        y = np.linspace(0, 1, 50) * corner_radius
        x = np.sqrt(corner_radius ** 2 - y ** 2)
        ax.plot(s * half_pitch_length - s * x, -half_pitch_width + y, lc, linewidth=linewidth)
        ax.plot(s * half_pitch_length - s * x, half_pitch_width - y, lc, linewidth=linewidth)
        # draw the D
        y = np.linspace(-1, 1, 50) * D_length  # D_length is the chord of the circle that defines the D
        x = np.sqrt(D_radius ** 2 - y ** 2) + D_pos
        ax.plot(s * half_pitch_length - s * x, y, lc, linewidth=linewidth)

    # remove axis labels and ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    # set axis limits
    xmax = field_dimen[0] / 2. + border_dimen[0]
    ymax = field_dimen[1] / 2. + border_dimen[1]
    ax.set_xlim([-xmax, xmax])
    ax.set_ylim([-ymax, ymax])
    #     ax.set_axisbelow(True)

    return fig, ax


def plot_ff(data_adjusted, ax):
    for player in data_adjusted:

        # Transform player location
        p_loc = transform_to_sck(player['x_opta'], player['y_opta'])
        ax.plot(p_loc[0],
                p_loc[1],
                'o',
                color='red' if player['team_status'] != 'defense' else 'blue',
                markersize=16,
                alpha=1.0,
                zorder=3)
        ax.quiver(p_loc[0], p_loc[1], player['vx'], player['vy'], scale=12., width=0.0015, headlength=5, headwidth=2,
                  zorder=10,
                  color='red' if player['team_status'] != 'defense' else 'blue', scale_units='inches')

        # Add Inner Marker for player With Opta Event
        if player['player_with_event']:
            ax.plot(p_loc[0],
                    p_loc[1],
                    'o',
                    color='k',
                    markersize=12,
                    alpha=1.0,
                    zorder=3)

        ax.annotate(f"{player['player_position']}", (p_loc[0],p_loc[1]), color='w', fontsize=7, va='center',ha='center')