import logging
import os
import time
from typing import Dict, Iterable, Optional

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

    def __init__(self, filepath: str, timeout: Optional[int] = 1) -> None:
        """Class for download school coords from OSM.

        Parameters
        ----------
        filepath : str
            Filepath to jsonline file
        timeout : Optional[int], optional
            Timeout between requests, by default 1 second
        """

        assert os.path.exists(filepath), f"Provided {filepath} does not exist."

        self.timeout = timeout
        self.filepath = filepath
        self.ID = "numer_rspo"
        self.api_results = None

    @staticmethod
    def __get_query_dict(row: dict, field_names: Iterable[str]) -> Dict[str, str]:
        return {field_name: str(row.get(field_name, "")) for field_name in field_names}

    @staticmethod
    def __create_api_request(query_dict: Dict[str, str]) -> Dict[str, str]:
        query = " ".join(query_dict.values())
        logging.debug(f"Query: {query}")
        response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()
        return response

    def __check_row(self, rspo_id: int):
        return rspo_id in self.api_results

    def run(self, results_filepath: str):
        if not os.path.exists(results_filepath):
            with open(results_filepath, "w") as _:
                pass

        with jsonlines.open(results_filepath, "r") as reader:
            self.api_results = {item[self.ID] for item in reader}

        data = pd.read_csv(self.filepath)
        for row_idx in tqdm(range(len(data))):
            row = data.iloc[row_idx]
            if self.__check_row(rspo_id=row[self.ID]):
                continue
            query = self.__get_query_dict(row, self.FIELD_NAMES)
            results = self.__create_api_request(query_dict=query)
            with jsonlines.open(results_filepath, "a") as writer:
                writer.write({self.ID: int(row[self.ID]), "content": results})
            time.sleep(self.timeout)


if __name__ == "__main__":
    scraper = CoordScraper(filepath="data/school_prep.jsonln", timeout=1)
    scraper.run("data/results.jsonln")
