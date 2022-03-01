from typing import Tuple, Union

import jsonlines
import pandas as pd
from tqdm import tqdm


class DummyPicker:
    def __init__(self, csv_filepath: str, coords_filepath: str, id_col):
        self.csv_filepath = csv_filepath
        self.coords_filepath = coords_filepath
        self.id_col = id_col

        with jsonlines.open(self.coords_filepath, "r") as reader:
            self.dataset = {row[self.id_col]: row["results"] for row in reader}

    def get_coords(self, rspo_code: int) -> Tuple[float, float]:
        if rspo_code in self.dataset.keys():
            row = self.dataset[rspo_code]
            if len(row["features"]) > 0:
                return row["features"][0]["geometry"]["coordinates"]

    def process(self, checkpoint) -> None:
        df = pd.read_csv(self.csv_filepath)
        for col in ("lat", "lng"):
            if col not in df:
                df[col] = None

        for row_idx in tqdm(range(len(df))):
            df_row = df.iloc[row_idx]
            values = self.get_coords(df_row[self.id_col])
            if values is None:
                continue

            lat, lng = values
            df.iloc[row_idx, df.columns.get_indexer(["lat", "lng"])] = lat, lng

            if row_idx % checkpoint == 0:
                df.to_csv(self.csv_filepath, index=False)


if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="Pick school coords from geocode data")
    arg_parser.add_argument("--csv_in_path", type=str, help="path to csv file to process", required=True)
    arg_parser.add_argument("--jsonln_in_path", type=str, help="path to jsonline file to process", required=True)
    arg_parser.add_argument("--id_col", type=str, defaul="numer_rspo", help="id column name", required=False)
    arg_parser.add_argument("--checkpoints_step", type=int, default=100, required=False)
    args = arg_parser.parse_args()

    picker = DummyPicker(csv_filepath=args.csv_in_path, coords_filepath=args.jsonln_in_path, id_col=args.id_col)
    picker.process(checkpoint=args.checkpoints)
