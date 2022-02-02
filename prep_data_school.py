import argparse
import os.path
import sys
from pathlib import PurePath, PurePosixPath
from posixpath import abspath, dirname
from typing import List, Optional

import pandas as pd
import unidecode
from numpy import dtype, str0


def remove_characters(input_text: str, chars_to_remove: List[str]) -> str:
    """Method for data preparation

    Parameters
    ----------
    input_text from df
    chars_to_remove in input_text
    """

    for char_to_remove in chars_to_remove:
        input_text = input_text.replace(char_to_remove, "")
    return input_text.strip()


def prep_data(path_input: str, path_output: Optional[str] = None):
    """Method for data preparation

    Parameters
    ----------
    path_input
        Input csv path
    path_output
        Optional output csv path
    """
    file_input = "school.csv"
    file_output = "school_prep.csv"
    # assert os.path.exists(path_input), "This file does not exist!"

    if not os.path.exists(path_input):
        # raise FileExistsError
        print("Sciezka nie istnieje!")

    if os.path.join(path_input, file_input) is None:
        print("Plik school.csv nie isnieje!")

    if path_output is None:
        path_output = os.path.join(path_input, file_output)
    else:
        path_output = os.path.join(path_output, file_output)

    path_input = os.path.join(path_input, file_input)

    try:
        df = pd.read_csv(path_input)

        col_name = {x: unidecode.unidecode(x).replace(" ", "_").lower() for x in df.columns}

        df.rename(columns=col_name, inplace=True)

        df[["gmina_typ", "gmina_cat"]] = df["gmina"].str.split(" ", 1, expand=True)

        for col in df.select_dtypes(["object"]).columns:
            df[col] = df[col].map(lambda x: remove_characters(str(x), ['"', "=", "(", ")"]))

        df.to_csv(path_output, index=False, encoding="utf-8")

    except FileNotFoundError:
        print("Not found file.")

    else:
        print(f"Dataset created, {path_output=}")


def marge_area_population(path_input: str, path_output: Optional[str] = None):
    """Method for data preparation

    Parameters
    ----------
    path_input
        Input csv path
    path_output
        Optional output csv path
    """

    data_files = [
        "school_prep.csv",
        "populations_area_province.csv",
        "populations_area_community.csv",
        "populations_area_district.csv",
    ]

    # assert all([os.path.exists(os.path.join(data_file)) for data_file in data_files])
    if not os.path.exists(path_input):
        # raise FileExistsError
        print("Sciezka nie istnieje!")

    if not all([os.path.join(path_input, data_file) for data_file in data_files]):
        print("No files to marge")

    if path_output is None:
        path_output = os.path.join(path_input)

    try:
        df_school = pd.read_csv(os.path.join(path_input, "school_prep.csv"))
        df_province = pd.read_csv(os.path.join(path_input, "populations_area_province.csv"))
        df_community = pd.read_csv(os.path.join(path_input, "populations_area_community.csv"))
        df_district = pd.read_csv(os.path.join(path_input, "populations_area_district.csv"))

        df_full = pd.merge(
            df_school.merge(
                df_province, how="left", left_on="kod_terytorialny_wojewodztwo", right_on="identyfikator"
            ).merge(
                df_district,
                how="left",
                left_on="kod_terytorialny_powiat",
                right_on="identyfikator",
                suffixes=("_prov", "_dist"),
            ),
            df_community,
            how="left",
            left_on="kod_terytorialny_gmina",
            right_on="identyfikator",
            suffixes=(None, "_comm"),
        )

        df_full.to_csv(os.path.join(path_output, "school_prep.csv"), index=False, encoding="utf-8")

    except FileNotFoundError:
        print("Not found files.")

    else:
        output_path = os.path.join(path_output, "school_prep.csv")
        print(f"Magres successfull, {output_path=}")


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(description="List the content of a folder")
    my_parser.add_argument("Path", metavar="path", type=str, help="Add path to prep dataset")

    args = my_parser.parse_args()

    input_path = args.Path
    input_path = abspath(dirname(input_path))

    if not os.path.exists(input_path):
        print("Sciezka nie istnieje!")
    else:
        prep_data(input_path)
        marge_area_population(input_path)
