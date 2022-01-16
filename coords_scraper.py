import re
from typing import Tuple

import requests


def get_school_coord(rspoValue: int) -> Tuple[float, float]:
    """Scrap school coords from https://rspo.gov.pl/rspo/{rspoValue}

    Args:
        rspo (int): The rspo value

    Returns:
        Tuple[float, float]: School coords (LAT, LNG)
    """

    MAP_POINT_PATTERN = re.compile(".*var map_point = (.*?);.*")
    response = requests.get(f"https://rspo.gov.pl/rspo/{rspoValue}", verify=False)

    location = MAP_POINT_PATTERN.search(response.text).groups()[0]
    lat = re.search(".*lat:([\d\.]+).*", location).groups()[0]
    lng = re.search(".*lng:([\d\.]+).*", location).groups()[0]
    return float(lat), float(lng)
