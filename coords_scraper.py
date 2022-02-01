import logging
import re
from typing import Tuple, Union

import requests


def get_school_coord(rspo_value: int) -> Union[None, Tuple[float, float]]:
    """Scrap school coords from https://rspo.gov.pl/rspo/{rspo_value}

    Args:
        rspo_value (int): The rspo value

    Returns:
        Union[None, Tuple[float, float]]: School coords (lat, lng)
    """

    MAP_POINT_PATTERN = re.compile(".*var map_point = (.*?);.*")
    response = requests.get(f"https://rspo.gov.pl/rspo/{rspo_value}", verify=False)
    try:
        search_location = MAP_POINT_PATTERN.search(response.text)
        location = search_location.groups()[0]
        lat = re.search(".*lat:([\d\.]+).*", location).groups()[0]
        lng = re.search(".*lng:([\d\.]+).*", location).groups()[0]
    except AttributeError:
        logging.warning(f"Could not find location details for rspoValue={rspo_value}")
        return
    return float(lat), float(lng)
