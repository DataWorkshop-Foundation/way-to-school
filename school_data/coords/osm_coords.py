import logging
import os
from typing import Dict, Iterable, Optional

import jsonlines
import requests


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

        with jsonlines.open(self.filepath, "r") as reader:
            for idx, row in enumerate(reader):
                logging.info(f"Row: {idx}")
                if self.__check_row(rspo_id=row[self.ID]):
                    continue
                else:
                    query = self.__get_query_dict(row, self.FIELD_NAMES)
                    results = self.__create_api_request(query_dict=query)
                    with jsonlines.open(results_filepath, "a") as writer:
                        writer.write({row[self.ID]: results})


if __name__ == "__main__":
    scraper = CoordScraper(filepath="data/school_prep.jsonln", timeout=1)
    scraper.run("data/results.jsonln")
