import logging
import os
import time
from typing import List, Optional

import pandas as pd
import requests


class CoordScraper:
    def __init__(self, filepath: str, timeout: Optional[int] = 1, checkpoint: Optional[int] = 50) -> None:
        assert os.path.exists(filepath), f"Provided {filepath} does not exist."

        self.checkpoint = checkpoint
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath)
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

    def create_checkpoint(self):
        self.df.to_csv(self.filepath)
        logging.info("Save data...")
        self.df = pd.read_csv(self.filepath)

    def query(self, row: pd.Series, *values) -> dict:
        return {value: str(row[value]) for value in list(values)}

    def get_coords(self, query_dict: dict) -> List[float]:
        query = " ".join([*query_dict.values()])
        logging.info("Query: ", query)
        response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()

        for idx, feature in enumerate(response["features"]):
            if feature["properties"]["osm_value"] in self.osm_values:
                coords = [coord for coord in response["features"][idx]["geometry"]["coordinates"]]

            if feature["properties"]["postcode"] != query_dict["kod_pocztowy"]:
                response["features"].pop(idx)

        if len(response["features"]) == 1:
            coords = [coord for coord in response["features"][0]["geometry"]["coordinates"]]
        if coords != 2:
            return None, None
        return coords

    def get_from_osm(self):
        try:
            for idx, row in self.df.iterrows():
                query_dict = self.query(
                    row,
                    "wojewodztwo",
                    "miejscowosc",
                    "ulica",
                    "numer_budynku",
                    "kod_pocztowy",
                )
                lat, lng = self.get_coords(query_dict)
                time.sleep(self.timeout)
                self.df.loc[idx, "lat"] = lat
                self.df.loc[idx, "lng"] = lng

                if idx % self.checkpoint == 0:
                    self.create_checkpoint()
                    exit(0)
        except Exception as e:
            logging.warning(e)


if __name__ == "__main__":
    scraper = CoordScraper("data/school_prep.csv")
    scraper.get_from_osm()
