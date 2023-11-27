# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/21 : 21:14
# @file : spider.py
# @SoftWare : PyCharm
import os.path
import random
import time

import requests
import logging.config
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from requests.exceptions import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor, wait

import functions.log as log
from functions.encrypt import Encrypt
from functions.constants import Constants

logging.config.dictConfig(log.getLogConfig("Spider"))
filepath = os.path.dirname(os.path.realpath(__file__))
console_logger = logging.getLogger("console_logger")


class Spider:

    def __init__(self, logger_name="console_logger"):
        if logger_name is None:
            self.logger = logging.getLogger("file_logger")
        else:
            self.logger = logging.getLogger(logger_name)
        self.header = {
            "user-agent": "smzdm_android_V10.6.10 rv:930 (TAS-AN00;Android7.1.2;zh)smzdmapp",
            "cookie": Spider.cookie_make()
        }
        self.col = None
        self.pool = ThreadPoolExecutor(max_workers=Constants.MAX_WORKERS)

    def _save(self, data, method="one", to='Mongo'):
        if to == 'Mongo':
            conn = MongoClient(Constants.MONGO_URL)
            smzdm_base = conn[Constants.DB_NAME]
            collection = smzdm_base[self.col]
            if method == "one":
                try:
                    collection.insert_one(data)
                except Exception as e:
                    if isinstance(e, DuplicateKeyError):
                        self.logger.warning(
                            f"Insert Collection {self.col} with DuplicateKeyError for {data.get('_id')}")
                    else:
                        self.logger.exception(f"Insert Collection {self.col} with Error: {e}")
                    return False
                else:
                    self.logger.info(f"Insert 1 Data into {Constants.DB_NAME}-{self.col}")
                    return True
            else:
                try:
                    collection.insert_many(data)
                except Exception as e:
                    if isinstance(e, DuplicateKeyError):
                        self.logger.warning(
                            f"Insert Collection {self.col} with DuplicateKeyError for {data.get('_id')}")
                    else:
                        self.logger.exception(f"Insert Collection {self.col} with Error: {e}")
                    return False
                else:
                    self.logger.info(f"Insert {len(data)} Data into {Constants.DB_NAME}-{self.col}")
                    return True

    def _search(self, filter_dict=None, method="many", to='Mongo'):
        if to == "Mongo":
            conn = MongoClient(Constants.MONGO_URL)
            smzdm_base = conn[Constants.DB_NAME]
            collection = smzdm_base[self.col]
            if method == "many":
                try:
                    cursor = collection.find(filter_dict)
                except Exception as e:
                    self.logger.exception(f"Find from Collection {self.col}: Error: {e}")
                    return []
                else:
                    return cursor
            else:
                try:
                    cursor = collection.find_one(filter_dict)
                except Exception as e:
                    self.logger.exception(f"Find from Collection {self.col}: Error: {e}")
                    return []
                else:
                    return cursor

    def _search_count(self):
        conn = MongoClient(Constants.MONGO_URL)
        smzdm_base = conn[Constants.DB_NAME]
        collection = smzdm_base[self.col]
        return collection.estimated_document_count()

    def _update(self, filter_dict, update_dict, method="one", to='Mongo'):
        if to == "Mongo":
            conn = MongoClient(Constants.MONGO_URL)
            smzdm_base = conn[Constants.DB_NAME]
            collection = smzdm_base[self.col]
            if method == "many":
                try:
                    result = collection.update_many(filter_dict, update_dict)
                except Exception as e:
                    self.logger.exception(f"Update data of Collection {self.col}: Error: {e}")
                    return False
                else:
                    self.logger.info(f"获得匹配的数据条数{result.matched_count}、影响的数据条数{result.modified_count}")
                    return True
            else:
                try:
                    result = collection.update_one(filter_dict, update_dict)
                except Exception as e:
                    self.logger.exception(f"Update data of Collection {self.col}: Error: {e}")
                    return False
                else:
                    self.logger.info(f"获得匹配的数据条数{result.matched_count}、影响的数据条数{result.modified_count}")
                    return True

    def crawl(self):
        pass

    @staticmethod
    def cookie_make():
        cookie = "".join(
            [k + '=' + v + ";" if isinstance(v, str) else k + '=' + str(v) + ";" for (k, v) in
             Constants.COOKIE_INFO.items()])
        return cookie


# 首先不考虑cookies的问题:直接使用抓包的

class UserIdSpiderAPP(Spider):

    def __init__(self, is_first=False, logger_name="console_logger"):
        super().__init__(logger_name)
        self.is_first = is_first

    def crawl(self):
        self.col = 'User_info'
        console_logger.info(f"Already have {self._search_count()} User Info Data in total".center(70, '='))
        console_logger.info("START CRAWLING".center(70, '='))
        self._check_first()
        self._main_loop()

    def _main_loop(self):
        while 1:
            users_before = self._search_count()
            searched_user_info_data = self._search(filter_dict={"is_used_for_search": False}, method='one')
            if searched_user_info_data is None:
                self.pool.shutdown()
                break
            searched_smzdm_id = searched_user_info_data.get("_id")
            console_logger.info(f"CRAWLING {searched_smzdm_id} RELATED IDS".center(70, '='))
            fans_ids = self._crawl_user_fans_or_followers(smzdm_id=searched_smzdm_id, category="fans")
            self.logger.info(f"Crawled User fans' ids Iterator of {searched_smzdm_id}")
            followers_ids = self._crawl_user_fans_or_followers(smzdm_id=searched_smzdm_id, category="followers")
            self.logger.info(f"Crawled User followers' ids Iterator of {searched_smzdm_id}")

            futures = self._crawl_fans_or_follower_helper(fans_ids)
            futures.extend(self._crawl_fans_or_follower_helper(followers_ids))
            if futures:
                wait(futures)
            users_after = self._search_count()
            self.logger.info(f"Collect and Insert {users_after} User Info Data in total")
            self._update(filter_dict={"_id": searched_smzdm_id}, update_dict={'$set': {"is_used_for_search": True}})
            console_logger.info(
                f"CRAWLED {searched_smzdm_id} RELATED {users_after - users_before} NEW IDS".center(70, '='))

    def _check_first(self):
        if self.is_first:
            ids = sum([self._crawl_ids_from_community(tab_name, tab_id) for (tab_name, tab_id) in
                       Constants.CATEGORY], [])
            for smzdm_id in ids:
                user_info_data = self._crawl_user_info(smzdm_id)
                self._save(data=user_info_data)
            self.logger.info(f"Collect and Insert {self._search_count()} User Info Data in total !!!!")

    def _crawl_fans_or_follower_helper(self, ids):
        futures = [self.pool.submit(self._crawl_user_info_and_save, smzdm_id) for smzdm_ids in ids for smzdm_id in
                   smzdm_ids]
        # pool.map(self._crawl_user_info_and_save, smzdm_ids, timeout=10)  # map方法
        # for smzdm_id in smzdm_ids:
        #     user_info_data = self._crawl_user_info(smzdm_id)
        #     self._save(data=user_info_data)
        return futures

    def _crawl_user_info_and_save(self, smzdm_id):
        existed = self._search(filter_dict={"_id": smzdm_id}, method='one')
        if existed is None:
            user_info_data = self._crawl_user_info(smzdm_id)
            self._save(data=user_info_data)

    def _crawl_ids_from_community(self, tab_name="全部", tab_id=0):
        url_community = Constants.URLS.get("community")
        if tab_id == 0:
            param_community = Constants.PARAMS_BASES.get("param_community_all_base")
        else:
            param_community = Constants.PARAMS_BASES.get("param_community_category_base")
        param_community.update({"tab_name": tab_name, "tab_id": tab_id})
        param = Encrypt.get_update_param(param_community)
        try:
            resp = requests.get(url=url_community, params=param, headers=self.header)
            time.sleep(random.random() * 2)
        except Exception as e:
            self.logger.exception(e)
            ids = None
        else:
            resp_json = resp.json()
            ids = [user.get('user_data').get("smzdm_id") for user in resp_json['data']['rows'] if
                   "discuss_num" not in user.keys()]
            self.logger.info(f"Crawled ids from {tab_name}")
        return ids

    def _crawl_user_info(self, smzdm_id):
        url_user_info = Constants.URLS.get("user_info")
        param_user_info = Constants.PARAMS_BASES.get("user_info_base")
        param_user_info['user_smzdm_id'] = smzdm_id
        param = Encrypt.get_update_param(param_user_info)
        # print(param)
        try:
            resp = requests.post(url=url_user_info, data=param, headers=self.header)
            time.sleep(random.random() * 2)
        except Exception as e:
            self.logger.exception(e)
            user_info_data = None
        else:
            # print(resp.json())
            data_json = resp.json().get("data")
            user_info_data = {
                "_id": smzdm_id,
                "is_used_for_search": False,
                "meta": data_json.get("meta"),
                "articles": data_json.get("articles"),
                "comments": data_json.get("comments"),
                "fans_num": data_json.get("fans_num"),
                "follower_num": data_json.get("follower_num"),
                "is_merchant": data_json.get("is_merchant"),
                "video_is_show": data_json.get("video_is_show"),
                "visitor_count": data_json.get("visitor_count"),
                "zhi": data_json.get("zhi"),
                "zan": data_json.get("zan"),
                "shoucang": data_json.get("shoucang"),
                "dashang": data_json.get("dashang"),
                "honor_desc": data_json.get("honor_desc"),
                "identity_type": data_json.get("identity_type"),
                "role": data_json.get("role"),
                "is_show_feed": data_json.get("is_show_feed"),
                "user_ip_addr": data_json.get("user_ip_addr"),
            }
            self.logger.info(f"Crawled User Info of {smzdm_id}")

        return user_info_data

    def _crawl_user_fans_or_followers(self, smzdm_id, category):
        """
        爬取用户的粉丝或者关注者的id，需要注意在每次更新offset时，都可能出现用户取消关注的行为，导致爬取数量与预期不一致
        :param smzdm_id: 目标用户id
        :param category: 爬取类别("fans" | "followers")
        :return: iterator[list[ids]]
        """
        url_user_fans_or_followers = Constants.URLS.get("user_" + category)
        param_user_fans_or_followers = Constants.PARAMS_BASES.get("user_fans_or_followers_base")
        param_user_fans_or_followers['target_smzdm_id'] = smzdm_id
        offset = 0
        while 1:
            param_user_fans_or_followers['offset'] = offset
            param = Encrypt.get_update_param(param_user_fans_or_followers)
            try:
                resp = requests.post(url=url_user_fans_or_followers, data=param, headers=self.header)
                time.sleep(random.random() * 2)
            except Exception as e:
                self.logger.exception(e)
                break
            else:
                try:
                    user_fans_or_followers = resp.json().get("data").get("rows")
                except JSONDecodeError as e:
                    console_logger.exception(f"JSONDecodeError happened with content", resp.content.decode())
                    break
                else:
                    total_num = int(resp.json().get("data").get("total"))
                    user_fans_or_followers_ids = [user_fans_or_followers_id.get("smzdm_id") for
                                                  user_fans_or_followers_id
                                                  in user_fans_or_followers]
                    crawled_num = len(user_fans_or_followers_ids)
                    if crawled_num == 0:
                        break
                    else:
                        offset += crawled_num
                        self.logger.info(f"Crawled {offset}/{total_num} User {category} ids of {smzdm_id}")
                        yield user_fans_or_followers_ids
                        if offset == total_num:  # 可能offset更新后，total_num减少导致小于offset
                            break
        console_logger.info(f"User {smzdm_id} have {offset} {category}".center(70, '='))


class UserIdSpiderHTML(Spider):
    """暂时搁置"""

    def __init__(self, is_first=False, logger_name=None):
        super().__init__(logger_name)
        self.url = ''
        self.is_first = is_first

    def crawl(self):
        if self.is_first:
            author_urls = self._crawl_ids_from_urls()
            return author_urls

    def _crawl_ids_from_urls(self):
        ids = self._crawl_urls_from_community()
        return ids

    def _crawl_urls_from_community(self):
        url = 'https://post.smzdm.com/json_more/'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        }
        author_urls = []
        tabs = [('shaiwu', 126), ('haowen', 124), ('zuixin', 135)]
        for filterUrl, tab_id in tabs:

            params = {
                'filterUrl': filterUrl,
                'tab_id': tab_id
            }
            try:
                resp = requests.get(url=url, params=params, headers=header)
                time.sleep(random.random() * 2)
            except Exception as e:
                self.logger.exception(e)
            else:
                data = resp.json()
                author_urls.extend([x.get('author_url') for x in data.get('data')])
                self.logger.info('Collected 24 author url')

        return author_urls
