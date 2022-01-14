import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree


def get_school_coord(rspo: int) -> None:

    response = requests.get(f"https://rspo.gov.pl/rspo/{rspo}", verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    dom = etree.HTML(str(soup))
    location = dom.xpath(
        "/html/body/div[1]/section/div/div/div[1]/div[2]/div/div[2]/div[9]/script"
    )[0].text.strip()

    location = location.replace("var map_point =  ", "")
    location = location.replace(";", "")
    location = location.replace(" ", "")

    location = location.replace("id", '"id"')
    location = location.replace("lat", '"lat"')
    location = location.replace("lng", '"lng"')
    coords = eval(location)

    return float(coords["lat"]), float(coords["lng"])


if __name__ == "__main__":
    df = pd.read_csv("data/school.csv")
    df["coords"] = df["Numer RSPO"].apply(lambda row: get_school_coord(row))
    df.to_csv("data/newSchool.csv", encoding="utf-8")
