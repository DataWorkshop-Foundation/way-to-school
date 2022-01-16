import os
import geopandas as geo
from geopandas import GeoDataFrame


class AdmUnits:
    def __init__(self, data_path: str):
        """Class for handling administrative geospatial data

        Parameters
        ----------
        data_path: str
            Path to geospatial data in .geojson format
        """

        assert os.path.exists(data_path), f"Provided {data_path=} does not exist."

        self.data_path = data_path
        self.geo_data = geo.read_file(self.data_path)
        self.__data_levels = set(self.geo_data["typ"])

    def __get_data(self, data_level: str) -> GeoDataFrame:
        assert data_level in self.__data_levels, f"Provided {data_level=} could not be found in data."
        return self.geo_data[self.geo_data["typ"] == data_level]
