from typing import Dict, Hashable, Tuple

import jsonlines
import pandas as pd
from tqdm import tqdm


class BasePicker:
    def __create_coords_dataset(self, coords_filepath: str, id_col: str) -> Dict[Hashable, Tuple[float, float]]:
        with jsonlines.open(coords_filepath, "r") as reader:
            dataset = {
                row[id_col]: tuple(row["results"]["features"][0]["geometry"]["coordinates"])
                for row in tqdm(reader, desc="Reading jsonl data...")
                if row["results"]["features"]
            }
        return dataset

    def process(self, csv_filepath: str, coords_filepath: str, id_col: str) -> None:
        dataset = self.__create_coords_dataset(coords_filepath=coords_filepath, id_col=id_col)
        df = pd.read_csv(csv_filepath)
        df[["lat", "lon"]] = pd.DataFrame(df[id_col].map(dataset).to_list(), index=df.index)
        df.to_csv(csv_filepath, index=False)


class SmarterPicker(BasePicker):
    def __create_coords_dataset(self, coords_filepath: str, id_col: str) -> Dict[Hashable, Tuple[float, float]]:
        raise NotImplementedError


if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="Pick school coords from geocode data")
    arg_parser.add_argument("--csv_in_path", type=str, help="path to csv file to process", required=True)
    arg_parser.add_argument("--jsonl_in_path", type=str, help="path to jsonl file to process", required=True)
    arg_parser.add_argument("--id_col", type=str, default="numer_rspo", help="id column name", required=False)
    args = arg_parser.parse_args()

    picker = BasePicker()
    picker.process(csv_filepath=args.csv_in_path, coords_filepath=args.jsonl_in_path, id_col=args.id_col)
