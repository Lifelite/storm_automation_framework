class StormTestData:

    def add_test_data(self, test_data: dict | object):
        """
        This method transforms provided dict or object into attributes for this class
        """
        if isinstance(test_data, dict):
            for key, value in test_data.items():
                self.__setattr__(key, value)

        else:
            self.__class__ = test_data

    def add_json_test_data(self, path: Path):
        with open(path, "r") as f:
            test_data = json.load(f)
            self.add_test_data(test_data)

    def add_csv_test_data(self, path: Path):
        with open(path, "r") as f:
            test_data = csv.DictReader(f)
            self.add_test_data(test_data)
