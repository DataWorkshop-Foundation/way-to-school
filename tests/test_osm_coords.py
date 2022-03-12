import unittest

from school_data.coords.osm_coords import CoordScraper


class TestCoordScraper(unittest.TestCase):
    def test_init(self):
        scraper = CoordScraper()
        self.assertIsInstance(scraper, CoordScraper)

    def test_run_wrong_in_filepath(self):
        filepath = "wrong/filepath.txt"
        scraper = CoordScraper()
        self.assertRaises(FileNotFoundError, scraper.run, filepath, "../data/test.jsonl")

    def test_run_wrong_id_col(self):
        scraper = CoordScraper()
        self.assertRaises(KeyError, scraper.run, "../data/school_prep.csv", "../data/test.jsonl", "wrong_id")


if __name__ == "__main__":
    unittest.main()
