import logging
import os
import time
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests
from tqdm import tqdm


class CoordScraper:
    FIELD_NAMES = [
        "wojewodztwo",
        "miejscowosc",
        "ulica",
        "numer_budynku",
        "kod_pocztowy",
    ]

    def __init__(self, timeout: Optional[int] = 1) -> None:
        """Class for download school coords from OSM.

        Parameters
        ----------
        timeout : Optional[int], optional
            Timeout between requests, by default 1 second
        """

        self.timeout = timeout
        self.osm_values = [
            "college",
            "kindergarten",
            "language_school",
            "library",
            "toy_library",
            "music_school",
            "school",
            "university",
        ]

    @staticmethod
    def __save_csv(data: pd.DataFrame, filepath: str):
        logging.info(f"Saving data to {filepath=}")
        data.to_csv(filepath, index=False)
        logging.info(f"Remaining {sum(data[['lat', 'lng']].isna().any(axis=1))} empty coords.")

    @staticmethod
    def __get_query_dict(row: pd.Series, field_names: Iterable[str]) -> Dict[str, str]:
        return {field_name: str(row.get(field_name, "")) for field_name in field_names}

    def get_coords(self, query_dict: Dict[str, str]) -> List[float]:
        """Download coords based on specific query details

        Parameters
        ----------
        query_dict : Dict[str, str]
            Query details

        Returns
        -------
        List[float]
            Returns school coordinates
        """
        query = " ".join(query_dict.values())
        logging.debug(f"Query: {query}")
        response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()

        if not response.get("features"):
            return None, None

        for feature in response["features"]:
            if all(
                [
                    feature["properties"]["osm_value"] in self.osm_values,
                    feature["properties"]["postcode"] == query_dict["kod_pocztowy"],
                ]
            ):
                return [coord for coord in feature["geometry"]["coordinates"]]

        return [coord for coord in response["features"][0]["geometry"]["coordinates"]]

    @staticmethod
    def __row_has_coords(row: pd.Series) -> bool:
        return not row[["lat", "lng"]].isna().any()

    def process_csv(self, filepath: str, checkpoint: int = 50):
        """Collect coordinates for .csv dataset

        Parameters
        ----------
        filepath: str
            File to process
        checkpoint: int
            Number of rows after which file will be overwritten
        """

        assert os.path.exists(filepath), f"Provided {filepath} does not exist."
        data = pd.read_csv(filepath)

        for col in ("lat", "lng"):
            if col not in data:
                data[col] = None

        for row_idx in tqdm(range(len(data))):
            row = data.iloc[row_idx]

            if self.__row_has_coords(row):
                continue

            time.sleep(self.timeout)
            query_dict = self.__get_query_dict(
                row=row,
                field_names=self.FIELD_NAMES,
            )
            lat, lng = self.get_coords(query_dict)

            if lat and lng:
                data.iloc[row_idx, data.columns.get_indexer(["lat", "lng"])] = lat, lng

            if row_idx % checkpoint == 0 or row_idx == len(data) - 1:
                self.__save_csv(data, filepath)


if __name__ == "__main__":
    scraper = CoordScraper(timeout=1)
    scraper.process_csv(
        filepath="/home/lsawaniewski/Documents/private/docs/DataWorkshop/DW_Olsztyn/repos/way-to-school/data/school_prep.csv",
        checkpoint=50,
    )
