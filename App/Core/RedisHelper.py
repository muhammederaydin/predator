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

import redis
import json
from .BaseHelper import BaseHelper

import logging
import sys
logger = logging.getLogger('redis')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class RedisHelper:

    def __init__(self, config, logger):
        self.response_code = None
        self.response_data = {}
        self.config = config
        self.logger = logger

        # Debug switch
        self.debug = True

        self.redis = None

        self.redis_host = self.config["host"]
        self.redis_port= self.config["port"]
        self.redis_db = self.config["db"]
        self.redis_connection()

    def redis_connection(self):
        try:
            self.redis = redis.StrictRedis(host=self.redis_host, 
                                           port=self.redis_port, 
                                           db=self.redis_db,
                                         charset="utf-8", decode_responses=True)
            self.logger.info("Redis Connection is Done !!!")
        except Exception as e:
            self.logger.error("Redis Connection Error : %s" % str(e))

    def get_redis_connection(self):
        return self.redis

    def to_byte(self, value):
        return redis.connection.Encoder(encoding='utf-8',
                                        encoding_errors='strict', 
                                        decode_responses=True).encode(value)

    def unique_add(self, key, value): #sadd
        key = self.to_byte(key)
        value = self.to_byte(value)
        self.redis.sadd(key, value)

    def increment(self, key):
        key = self.to_byte(key)
        self.redis.incr(key)

    def insert_sequential(self, key, value):
        key = self.to_byte(key)
        value = self.to_byte(value)
        self.redis.rpush(key, value)

    def pop_sequential(self, key):
        key = self.to_byte(key)
        return self.redis.rpop(key)

    def get_list_key_last_value(self, key):
        key = self.to_byte(key)
        key_list_length = self.get_len_list_key(key)
        if key_list_length == -1:
            last_value = "-1"
        else:
            last_value = self.redis.lindex(key, key_list_length - 1)

        return last_value

    def get_len_list_key(self, key):
        key = self.to_byte(key)
        if self.redis.exists(key):
            lenght_list = self.redis.llen(key)
            return lenght_list
        else:
            return -1

    def insert_hash(self, hash, key, value): #Hash
        key = self.to_byte(key)
        value = self.to_byte(value)
        hash = self.to_byte(hash)
        self.redis.hset(hash, key, value)

    def get_hash_value(self, hash):
        hash = self.to_byte(hash)
        return self.redis.hgetall(hash)

    def get_keys(self, search_key_expression):
        result = self.redis.keys(pattern=search_key_expression)
        return result

    def get_key_unique_value(self, key):
        key = self.to_byte(key)
        result = self.redis.smembers(key)
        return list(result)

    def get_key_unique_value_count(self, key):
        key = self.to_byte(key)
        result = self.redis.scard(key)
        return result

    def get_key_value(self, key):
        key = self.to_byte(key)
        result = self.redis.get(key)
        return result

    def get_key_list_all_element(self, key):
        key = self.to_byte(key)
        key_list_length = self.get_len_list_key(key)
        list_elements = self.redis.lrange(key, 0, key_list_length - 1)
        return list_elements

    def set_key_value(self, key, value):
        key = self.to_byte(key)
        if isinstance(value, list):
            value = str(value)
        else:
            value = self.to_byte(value)
        self.redis.set(key, value)

    def check_if_exist(self, key):
        return self.redis.exists(key)

    def set_key_expire(self, key, time):
        self.redis.expire(key, time)
