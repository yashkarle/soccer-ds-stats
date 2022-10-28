import glob
import os
import json


"""
    file 2
    Creating dataframe from freeze frames files
    Iterating through all freeze frame file and create .json file
    with a unique Id for each freeze frames to match it with the event
 
    The gerneated file is very large. Since it contains all freeze frames. You may want to create
    file for indiviudal teams or matches.
    
 """

from settings import prefix, DATA_FOLDER_FF, pattern_match, PROCESSED_FOLDER, ff_output_name

if __name__ == '__main__':

    ff_dict = dict()
    for match_file in glob.glob(DATA_FOLDER_FF + f'/*{prefix}'):
        match_id = os.path.basename(match_file).split(prefix)[0]
        print(match_id)
        with open(f"{match_file}", 'r') as in_file:
            freeze_frame = json.load(in_file)
            for ff in freeze_frame:
                ff_dict[pattern_match.format(match_id, ff['event_id'])] = [{k: v for k,
                                                                                     v in x.items() if k in ['x_opta',
                                                                                                             'y_opta',
                                                                                                             'player_id',
                                                                                                             'team',
                                                                                                             'player_position',
                                                                                                             'vx', 'vy',
                                                                                                             'team_status',
                                                                                                             'ax', 'ay',
                                                                                                             'player_with_event']}
                                                                           for x in ff['adjusted_data']]
    # Persist Freeze Frames
    with open(f"{PROCESSED_FOLDER}/{ff_output_name}.json", 'w') as f:
        f.write(json.dumps(ff_dict, separators=(',', ':')))