import logging
import os
import time
from typing import Dict, Iterable, Optional, Any, Hashable

import jsonlines
import pandas as pd
import requests
from tqdm import tqdm

from pprint import pprint

from helpers.np_encode import cast_to_serializable


class CoordScraper:
    FIELD_NAMES = [
        "wojewodztwo",
        "miejscowosc",
        "ulica",
        "numer_budynku",
        "kod_pocztowy",
    ]

    def __init__(self, timeout: int = 1,  checkpoint_steps: int = 100) -> None:
        """Class for download school coords from OSM.

        Parameters
        ----------
        timeout : int
            Timeout between requests, by default 1 second
        checkpoint_steps: int
            Steps to perform between each results save
        """

        self.timeout = timeout
        self.checkpoint_steps = checkpoint_steps

    @staticmethod
    def __get_query_dict(row: pd.Series, field_names: Iterable[str]) -> Dict[str, str]:
        return {field_name: str(row.get(field_name, "")) for field_name in field_names}

    @staticmethod
    def __create_api_request(query_dict: Dict[str, str]) -> Dict[str, str]:
        query = " ".join(query_dict.values())
        logging.debug(f"Query: {query}")
        response = requests.get(f"https://photon.komoot.io/api/?q={query}").json()
        return response

    def run(self, in_filepath: str, out_filepath: str, id_col: str = "numer_rspo"):
        """Process csv with school data and save geocoding results in jsonlines format

        Parameters
        ----------
        in_filepath : str
            Filepath to input csv file
        out_filepath : str
            Filepath to output jsonline file
        id_col: str
            Unique keys column name
        """

        assert os.path.exists(in_filepath), f"Provided {in_filepath=} does not exist."
        data = pd.read_csv(in_filepath)

        if os.path.exists(out_filepath):
            with jsonlines.open(out_filepath, "r") as reader:
                api_results = {item[id_col]: item for item in reader}
        else:
            api_results = {}

        for row_idx in tqdm(range(len(data))):
            row = data.iloc[row_idx]

            if row[id_col] in api_results:
                continue

            query = self.__get_query_dict(row, self.FIELD_NAMES)
            query_results = self.__create_api_request(query_dict=query)

            if query_results:
                api_results[row[id_col]] = {id_col: cast_to_serializable(row[id_col]), "results": query_results}

            time.sleep(self.timeout)

            if row_idx % self.checkpoint_steps == 0:
                self.__save_results_jsonl(api_results, out_filepath)

        self.__save_results_jsonl(api_results, out_filepath)

    @staticmethod
    def __save_results_jsonl(data: Dict[Hashable, Dict[Hashable, Any]], filepath: str):
        pprint(data)
        with jsonlines.open(filepath, "w") as writer:
            writer.write_all(data.values())


if __name__ == "__main__":
    import argparse
    import os

    arg_parser = argparse.ArgumentParser(description='Geocode data with OSM API')
    arg_parser.add_argument('--in_path', type=str, help='path to csv file to process', required=True)
    arg_parser.add_argument('--out_path', type=str, help='path to jsonl output file', required=True)
    arg_parser.add_argument('--id_col', type=str, default="numer_rspo", help='id column name', required=False)
    arg_parser.add_argument('--timeout', type=int, default=1, required=False)
    arg_parser.add_argument('--checkpoint_steps', type=int, default=100, required=False)
    args = arg_parser.parse_args()

    input_path = os.path.abspath(args.in_path)
    output_path = os.path.abspath(args.out_path)

    scraper = CoordScraper(timeout=args.timeout, checkpoint_steps=args.checkpoint_steps)
    scraper.run(in_filepath=input_path, out_filepath=output_path, id_col=args.id_col)
