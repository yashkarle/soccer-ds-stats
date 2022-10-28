import json
import glob
import os


def qualifier_value(qualifiers, qualifier_id):

    for q in qualifiers:
        if q['qualifierId'] == qualifier_id:
            return float(q['value'])
    return None


def list_of_match_files(folder_path):
    """
    Returns list of raw files
    :param only_tournaments:
    :return: list of raw files
    """

    data_list = list()
    for match_file in glob.glob(folder_path + '/events/*.json'):
        match_id = os.path.basename(match_file).split('.json')[0]

        data_list.append({
            'match_id': match_id,
            'path': match_file
        })
    return data_list


def get_event_chains(full_path):
    with open(full_path, 'r', encoding="utf-8") as json_string:
        return json.load(json_string)


def transform_to_sck(x_opta, y_opta, field_dimen=(105, 68)):
    """
    Tranform Opta Coordinates to Skillcorner Coordinates
    :param x_opta:
    :param y_opta:
    :param field_dimen:
    :return:
    """
    start_x = ((field_dimen[0] / 100) * x_opta) - (field_dimen[0] / 2)
    start_y = ((field_dimen[1] / 100) * y_opta) - (field_dimen[1] / 2)
    return [start_x, start_y]