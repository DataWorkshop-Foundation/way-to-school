from typing import Tuple, Union

import jsonlines
import pandas as pd
from tqdm import tqdm


class DummyPicker:
    def __init__(self, csv_filepath: str, coords_filepath: str):
        self.csv_filepath = csv_filepath
        self.coords_filepath = coords_filepath

        with jsonlines.open(self.coords_filepath, "r") as reader:
            self.dataset = {row["numer_rspo"]: row["results"] for row in reader}

    def get_coords(self, rspo_code: int):
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
            values = self.get_coords(df_row["numer_rspo"])
            if values is None:
                continue

            lat, lng = values
            df.iloc[row_idx, df.columns.get_indexer(["lat", "lng"])] = lat, lng

            if row_idx % checkpoint == 0:
                df.to_csv(self.csv_filepath, index=False)


if __name__ == "__main__":
    picker = DummyPicker("data/school_prep.csv", "data/school_data.jsonln")
    picker.process(checkpoint=50)
