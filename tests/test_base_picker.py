import unittest
from school_data.coords.coord_picker import BasePicker


class TestBasePicker(unittest.TestCase):
    def test_init(self):
        """
        Class instance class
        """
        picker = BasePicker()
        self.assertIsInstance(picker, BasePicker)


if __name__ == "__main__":
    unittest.main()
