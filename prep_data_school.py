import os.path
from pathlib import PurePath, PurePosixPath
from typing import List

import pandas as pd
import unidecode


def clean_text(input_text: str) -> str:  # nazwa argumentu nic nie mówi
    return str(input_text).replace("=", "").replace('"', "")


def remove_characters(input_text: str, chars_to_remove: List[str]) -> str:
    for char_to_remove in chars_to_remove:
        input_text = input_text.replace(char_to_remove, "")
    return input_text


def prep_data(path_input: str, path_output: Optional[str] = None):
    """Method for data preparation

    Parameters
    ----------
    path_input
        Input csv file path
    """

    # assert os.path.exists(path_input), "This file does not exist!"
    if not os.path.exists(path_input):
        # raise FileExistsError
        print("Nie istnieje!")

    if path_output is None:
        path_output = path_input.replace(".csv", "_prep.csv")

    try:
        df = pd.read_csv(path_input)

        col_name = {}

        for i in df.columns: # for col_name in ...
            col_name[i] = unidecode.unidecode(i).replace(" ", "_").lower()

        col_name = {x: unidecode.unidecode(x).replace(" ", "_").lower() for x in df.columns}

        df.rename(columns=col_name, inplace=True)

        for col in df.select_dtypes(["object"]).columns:
            df[col] = df[col].map(lambda x: clean_text(x))

        df["gmina_typ"] = df.gmina.map(lambda x: x.split("(")[1].replace(")", ""))

        df["gmina_cat"] = df.gmina.map(lambda x: x.split("(")[0].replace(")", ""))

        df.to_csv(path_input.replace(".csv", "_prep.csv"), index=False, encoding="utf-8")

    except FileNotFoundError:
        print("Not found file.")

    else:
        print(f'Dataset created, PATH: {path_input.replace(".csv", "_prep.csv")}')


def marge_area_population(path_input):

    # data_files = ("populations_area_province", "populations_area_province")
    # assert all([os.path.exists(os.path.join(data_file)) for data_file in data_files])

    try:
        p = PurePath(path_input)
        path = p.parents[0]

        name = PurePosixPath(path_input).stem
        name = name + "_prep.csv"
        full_path = path.joinpath(name)

        if PurePath(path) == PurePath():

            df_school = pd.read_csv(name)
            df_province = pd.read_csv("populations_area_province.csv")
            df_community = pd.read_csv("populations_area_community.csv")
            df_district = pd.read_csv("populations_area_district.csv")

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
            df_full.to_csv(name, index=False, encoding="utf-8")

        else:
            df_school = pd.read_csv(full_path)
            df_province = pd.read_csv(path.joinpath("populations_area_province.csv"))
            df_community = pd.read_csv(path.joinpath("populations_area_community.csv"))
            df_district = pd.read_csv(path.joinpath("populations_area_district.csv"))

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
            df_full.to_csv(full_path, index=False, encoding="utf-8")

    except FileNotFoundError:
        print("Not found files.")

    else:
        output_path = path_input.replace(".csv", "_prep.csv")
        print(f'Magres successfull, PATH: {output_path=}')


if __name__ == "__main__":
    # tu robimy coś jeśli to jest nasz punkt wejścia
    path = "abc" # tu chwytamy z argparsa ścieżkę
    prep_data(path)
    marge_area_population(path)
