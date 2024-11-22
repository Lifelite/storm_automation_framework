import csv
import json
import logging
import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime
from os import PathLike
from pathlib import Path


@dataclass
class StormTestData:
    correlation_id: uuid.UUID = uuid.uuid4()
    csv_path: Path | str = None
    json_path: Path | str = None
    backup_path: Path | str = os.path.join(os.getcwd(), 'backups')
    csv_row_data = []

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
        self.json_path = path
        with open(path, "r") as f:
            test_data = json.load(f)
            self.add_test_data(test_data)

    def add_csv_test_data(self, path: Path, key:str = None):
        logging.info(f"Adding test data from {path}")
        if self.csv_path is not None:
            logging.warning(f"Overwriting test data from {self.csv_path}.  This will overwrite existing test data.\n"
                            f"It is recommended to create a new class instance rather than overwriting.")
        self.csv_path = path
        with open(path, "r") as f:
            test_data = csv.DictReader(f)
            duplicates = 0
            for row in test_data:
                class_instance = StormTestData()
                if getattr(row, key or '', False):
                    if getattr(self, key, False):
                        duplicates += 1
                        new_key = f"{key}_{str(duplicates)}"
                        logging.warning(f"Duplicate key found.  Adding data as {new_key}.")
                        class_instance.add_test_data(row)
                        setattr(self, new_key, class_instance)
                    class_instance.add_test_data(row)
                    setattr(self, key, class_instance)
                elif key is not None:
                    logging.warning(f"{key} is not a valid header value in {path}. Data is added to csv_row_data")
                else:
                    logging.info(f"No key provided, adding test data to csv_row_data")
                self.csv_row_data.append(class_instance)

    def update_csv_test_data(self):
        root = os.getcwd()
        if "backup" not in os.listdir(root):
            os.mkdir(self.backup_path)
        try:
            shutil.copy(self.csv_path, self.backup_path)
        except FileNotFoundError:
            self.csv_path = os.path.join(root, f"StormTestData_{datetime.now()}.csv")
            logging.error(f"Could not find {self.csv_path}.  Writing new file")
        with open(self.csv_path, "w") as csv_file:
            class_dict = self.__dict__.copy()
            class_dict.pop("__class__")
            csv_writer = csv.DictWriter(csv_file, fieldnames=class_dict.keys())
            csv_writer.writeheader()
            for items in class_dict.keys():
                csv_writer.writerows(class_dict[items])

    def update_json_test_data(self):
        root = os.getcwd()
        if "backup" not in os.listdir(root):
            os.mkdir(self.backup_path)
        try:
            shutil.copy(self.json_path, self.backup_path)
        except FileNotFoundError:
            self.json_path = os.path.join(root, f"StormTestData_{datetime.now()}.json")
            logging.error(f"Could not find {self.json_path}.  Writing new file")
        with open(self.json_path, "r") as json_file:
            class_dict = self.__dict__.copy()
            class_dict.pop("__class__")
            json_data = json.dumps(class_dict)
            json_file.write(json_data)







    # def update_test_data(self, test_data: dict):
