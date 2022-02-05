import random
import time
from audioop import add

import pandas as pd
import urllib3

from coords_scraper import get_coords_from_osm

# Disable https warning
urllib3.disable_warnings()

CHECKPOINT = 50

if __name__ == "__main__":
    df = pd.read_csv("data/school_prep.csv", index_col=0)

    for index, row in df.iterrows():
        lat, lng = get_coords_from_osm(
            row["miejscowosc"], street=row["ulica"], address=row["numer_budynku"], orginal_postcode=row["kod_pocztowy"]
        )
        time.sleep(2)

        df.loc[index, "lat"] = lat
        df.loc[index, "lng"] = lng

        if index % CHECKPOINT == 0:
            df.to_csv("data/school_with_coords.csv")
