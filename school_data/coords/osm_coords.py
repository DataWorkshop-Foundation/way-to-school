import logging
import os
import time
from typing import Dict, Iterable, List, Optional, Union

import jsonlines
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
    def __save_jsonln(row_idx: int, data, filepath: str) -> None:
        logging.info(f"Saving data to {filepath=}")
        with jsonlines.open(filepath, mode="a") as writer:
            writer.write({row_idx: data})

    @staticmethod
    def __get_query_dict(row: pd.Series, field_names: Iterable[str]) -> Dict[str, str]:
        return {field_name: str(row.get(field_name, "")) for field_name in field_names}

    @staticmethod
    def __get_api_results(query_dict: Dict[str, str]) -> Dict[str, str]:
        query = " ".join(query_dict.values())
        logging.debug(f"Query: {query}")
        response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()
        return response

    @staticmethod
    def __row_has_coords(row: pd.Series) -> bool:
        return not row[["lat", "lng"]].isna().any()

    @staticmethod
    def __load_api_response(row_idx: int, output_filepath: str) -> Union[None, Dict]:
        with jsonlines.open(output_filepath) as reader:
            for obj in reader.iter():
                if row_idx in obj.keys():
                    return obj[row_idx]
                return None

    def get_coords(self, query_dict: Dict[str, str], response_dict: Dict[str, str]) -> List[float]:
        """Download coords based on specific query details

        Parameters
        ----------
        query_dict : Dict[str, str]
            Query details
        response_dict: Dict[str, str]
            Api response
        Returns
        -------
        List[float]
            Returns school coordinates
        """

        if not response_dict.get("features"):
            return None, None

        for feature in response_dict["features"]:
            if all(
                [
                    feature["properties"]["osm_value"] in self.osm_values,
                    feature["properties"]["postcode"] == query_dict["kod_pocztowy"],
                ]
            ):
                return [coord for coord in feature["geometry"]["coordinates"]]

        return [coord for coord in response_dict["features"][0]["geometry"]["coordinates"]]

    def process_csv(self, filepath: str, output_filepath: str, checkpoint: int = 50):
        """Collect coordinates for .csv dataset

        Parameters
        ----------
        filepath: str
            File to process
        output_filepath: str
            Filepath to save api response
        checkpoint: int
            Number of rows after which file will be overwritten
        """

        assert os.path.exists(filepath), f"Provided {filepath} does not exist."
        if not os.path.exists(output_filepath):
            logging.debug(f"Provided {filepath} does not exists. Create file...")
            _ = open(output_filepath, "w")

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
            query_response = self.__load_api_response(row_idx, output_filepath)
            if query_response is None:
                query_response = self.__get_api_results(query_dict=query_dict)
                self.__save_jsonln(row_idx, query_response, output_filepath)
            lat, lng = self.get_coords(query_dict, query_response)

            if lat and lng:
                data.iloc[row_idx, data.columns.get_indexer(["lat", "lng"])] = lat, lng

            if row_idx % checkpoint == 0 or row_idx == len(data) - 1:
                self.__save_csv(data, filepath)


if __name__ == "__main__":
    scraper = CoordScraper(timeout=1)
    scraper.process_csv(
        filepath="data/school_prep.csv",
        output_filepath="data/output.jsonl",
        checkpoint=50,
    )
