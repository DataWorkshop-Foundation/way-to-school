from pathlib import PurePath, PurePosixPath

import pandas as pd
import unidecode


def clean_text(x):
    return str(x).replace("=", "").replace('"', "")


def prep_data(path_input):
    try:
        df = pd.read_csv(path_input)

        col_name = {}

        for i in df.columns:
            col_name[i] = unidecode.unidecode(i).replace(" ", "_").lower()

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
        print(f'Magres successfull, PATH: {path_input.replace(".csv", "_prep.csv")}')
