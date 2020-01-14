#MIT License

#Copyright (c) 2020 Emin Muhammed Eraydın

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import re
import json
import logging

from pymongo import MongoClient


class MongoDBHelper:

    def __init__(self, config):
        self.response_code = None
        self.response_data = {}
        self.config = config

        self.db_address = self.config["db_address"]
        self.db_address_uri = self.config["db_address_uri"]
        self.db_port = int(self.config["db_port"])
        self.db_user = self.config["db_user"]
        self.db_pwd = self.config["db_pwd"]
        self.db_name = self.config["db_name"]
        self.connection = None

        self.authenticate_mongo_connection()

    def mongo_connection(self):
        try:
            self.connection = MongoClient(self.db_address, self.db_port)
            logging.info("MongoDB Connection is Done !!!")

        except Exception as e:
            logging.error("MongoDB Connection Error: {}".format(str(e)))
            raise Exception("MongoDB Connection Error: {}".format(str(e)))

    def authenticate_mongo_connection(self):
        try:
            connection = MongoClient(self.db_address_uri)
            self.connection = connection[self.db_name]
            self.connection.authenticate(self.db_user, self.db_pwd)
            logging.info("MongoDB Connection is Done !!!")

        except Exception as e:
            logging.error("MongoDB Auth Connection Error: {}".format(str(e)))
            raise Exception("MongoDB Auth Connection Error: {}".format(str(e)))
    
    def get_connection(self):
        return self.connection

    def run_query(self, query):
        try:
            self.result_list = []
            self.result = self.connection.find(query[0], {'_id': False})
            for i in self.result:
                self.result_list.append(json.dumps(i))
            logging.info("MongoDB Run Filter Query is Done")
        except Exception as e:
            logging.error("MongoDB Run Filter Query Error: {}".format(str(e)))
            raise Exception("MongoDB run Filter Query Error: {}".format(str(e)))

    def insert_to_mongo(self, collection, data):
        try:
            collection = self.connection[str(collection)]
            _insert = collection.insert(data)
            logging.info("Insert Done")
        except exception as e:
            logging.error("Insert to MongoDB Error: {}".format(str(e)))
            raise Exception("Insert to MongoDB Error: {}".format(str(e)))


