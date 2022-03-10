import unittest

from school_data.coords.coord_picker import BasePicker


class TestBasePicker(unittest.TestCase):
    csv_filepath = "data/school_prep.csv"

    def test_init(self):
        """
        Test instance class
        """
        picker = BasePicker()
        self.assertIsInstance(picker, BasePicker)

    def test_wrong_coords_filepath(self):
        """
        Test wrong coords filepath
        """
        picker = BasePicker()
        self.assertRaises(
            FileNotFoundError, picker.process, "../data/school_prep.csv", "wrong/path/test.jsonl", "numer_rspo"
        )

    def test_wrong_csv_filepath(self):
        """
        Test wrong csv filepath
        """
        picker = BasePicker()
        self.assertRaises(
            FileNotFoundError, picker.process, "data/wrong/school_prep.csv", "../data/school_data.jsonl", "numer_rspo"
        )


if __name__ == "__main__":
    unittest.main()
