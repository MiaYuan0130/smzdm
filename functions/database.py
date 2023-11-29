# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/29 : 11:23
# @file : database.py
# @SoftWare : PyCharm

import logging.config
from abc import abstractmethod
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import functions.log as log

from functions.constants import Constants

logging.config.dictConfig(log.getLogConfig("Database"))


class Database:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger("Database")

    @abstractmethod
    def save(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def search(self, *args, **kwargs):
        pass


class Mongo(Database):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = kwargs.get("collection_name", "User_info")
        self.connection = MongoClient(Constants.MONGO_URL)
        self.smzdm_base = self.connection[Constants.DB_NAME]
        self.collection = self.smzdm_base[self.collection_name]

    def save(self, data, method='one'):
        if method == "one":
            try:
                self.collection.insert_one(data)
            except Exception as e:
                if isinstance(e, DuplicateKeyError):
                    self.logger.warning(
                        f"Insert Collection {self.collection_name} with DuplicateKeyError for {data.get('_id')}")
                else:
                    self.logger.exception(f"Insert Collection {self.collection_name} with Error: {e}")
                return False
            else:
                self.logger.info(f"Insert 1 Data into {Constants.DB_NAME}-{self.collection_name}")
                return True
        else:
            try:
                self.collection.insert_many(data)
            except Exception as e:
                if isinstance(e, DuplicateKeyError):
                    self.logger.warning(
                        f"Insert Collection {self.collection_name} with DuplicateKeyError for {data.get('_id')}")
                else:
                    self.logger.exception(f"Insert Collection {self.collection_name} with Error: {e}")
                return False
            else:
                self.logger.info(f"Insert {len(data)} Data into {Constants.DB_NAME}-{self.collection_name}")
                return True

    def search(self, filter_dict=None, method="many"):
        if method == "many":
            try:
                cursor = self.collection.find(filter_dict)
            except Exception as e:
                self.logger.exception(f"Find from Collection {self.collection_name}: Error: {e}")
                return []
            else:
                return cursor
        else:
            try:
                cursor = self.collection.find_one(filter_dict)
            except Exception as e:
                self.logger.exception(f"Find from Collection {self.collection_name}: Error: {e}")
                return []
            else:
                return cursor

    def search_count(self):
        return self.collection.estimated_document_count()

    def update(self, filter_dict, update_dict, method="one"):
        if method == "many":
            try:
                result = self.collection.update_many(filter_dict, update_dict)
            except Exception as e:
                self.logger.exception(f"Update data of Collection {self.collection_name}: Error: {e}")
                return False
            else:
                self.logger.info(f"获得匹配的数据条数{result.matched_count}、影响的数据条数{result.modified_count}")
                return True
        else:
            try:
                result = self.collection.update_one(filter_dict, update_dict)
            except Exception as e:
                self.logger.exception(f"Update data of Collection {self.collection_name}: Error: {e}")
                return False
            else:
                self.logger.info(f"获得匹配的数据条数{result.matched_count}、影响的数据条数{result.modified_count}")
                return True
