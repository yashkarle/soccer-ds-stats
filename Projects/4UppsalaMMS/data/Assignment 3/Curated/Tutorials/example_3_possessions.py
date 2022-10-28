"""
    Creating Dataframe dataset from Possesion Chains
    Iterating through all possession in all the matches and create single row for each event,
    which contains informaiton about event and outcome of the possession chain
    
    This can be used (for example) for fitting value model for possession chains.
    
    In the example, we just do it for first 10 matches.
"""


import pandas as pd
import matplotlib.pyplot as plt

from helper import list_of_match_files, get_event_chains, qualifier_value
from settings import DATA_FOLDER_PC, PROCESSED_FOLDER, df_output_name

if __name__ == '__main__':

    data_set = list()

    # Get All Matches
    matches = list_of_match_files(DATA_FOLDER_PC)

    for match in matches[0:2]:

        # Get Possession Chains From All Matches
        event_chains = get_event_chains(match['path'])

        # Events in Possession Chains
        chain_id = 0
        for chain in event_chains:

            # Iterate All Events in Chain
            for event in chain:
                data_set.append({
                    'match_id': int(match['match_id']),
                    'type': int(event['eventTypeId']),
                    'team_id': int(event['teamId']),
                    'player_id': int(event['playerId']) if 'playerId' in event else -1,
                    'description': event['description'] if 'description' in event else '',
                    'event_id': int(event['eventId']),
                    'outcome': int(event['outcome']),
                    'x': float(event['x']),
                    'y': float(event['y']),
                    'x2': qualifier_value(event['qualifiers'], 140),
                    'y2': qualifier_value(event['qualifiers'], 141),
                    'goal': 1 if chain[-1]['eventTypeId'] in [16] else 0, # Last Event Goal
                    'shot': 1 if chain[-1]['eventTypeId'] in [13,14,15,16] else 0, # Last Event Shot
                    'chain_id': chain_id


                })
            chain_id +=1

    # Create Data Frame
    df = pd.DataFrame(data_set)

    df.to_csv(f"{PROCESSED_FOLDER}/{df_output_name}.csv",index=None)

    # Plot Some Values
    df.goal.value_counts().plot(kind='bar')  # Goals
    plt.show()

    df.shot.value_counts().plot(kind='bar')  # Shots
    plt.show()

    df.type.value_counts().plot(kind='bar') # Event Types
    plt.show()

