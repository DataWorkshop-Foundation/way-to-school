import logging
import random
import re
import time
from typing import Tuple, Union

import requests


def get_school_coord(
    rspo_value: int, min_sleep_time: int = 1, max_sleep_time: int = 5
) -> Union[None, Tuple[float, float]]:
    """Scrap school coords from https://rspo.gov.pl/rspo/{rspo_value}

    Args:
        rspo_value (int): The rspo value

    Returns:
        Union[None, Tuple[float, float]]: School coords (lat, lng)
    """

    MAP_POINT_PATTERN = re.compile(".*var map_point = (.*?);.*")
    response = requests.get(f"https://rspo.gov.pl/rspo/{rspo_value}", verify=False)
    time.sleep(random.randint(min_sleep_time, max_sleep_time))
    try:
        search_location = MAP_POINT_PATTERN.search(response.text)
        location = search_location.groups()[0]
        lat = re.search(".*lat:([\d\.]+).*", location).groups()[0]
        lng = re.search(".*lng:([\d\.]+).*", location).groups()[0]
    except AttributeError:
        logging.warning(f"Could not find location details for https://rspo.gov.pl/rspo/{rspo_value}")
        return
    return float(lat), float(lng)


def get_coords_from_osm(city: str, street: str, address: str, orginal_postcode: str):
    query = f"{city} {street} {address} {orginal_postcode}"
    response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()
    is_school = False
    coordinates = [None, None]
    for i in range(len(response["features"])):
        if not is_school:
            try:
                if response["features"][i]["properties"]["osm_value"] in [
                    "college",
                    "kindergarten",
                    "language_school",
                    "library",
                    "toy_library",
                    "music_school",
                    "school",
                    "university",
                ]:
                    coordinates = response["features"][i]["geometry"]["coordinates"]
                    is_school = True
                else:
                    coordinates = response["features"][0]["geometry"]["coordinates"]
            except AttributeError:
                logging.warning(f"Could not find location details for https://rspo.gov.pl/rspo/{query}")
    return coordinates
