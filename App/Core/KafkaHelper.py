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

import threading
from kafka import KafkaConsumer, KafkaProducer
import json
from .BaseHelper import BaseHelper

import logging
import sys
logger = logging.getLogger('kafka')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class KafkaHelper(BaseHelper):

    def __init__(self, config, logger, redis, db_helper):
        try:
            self.config = config
            self.logger = logger
            self.redis = redis
            self.db_helper = db_helper
            super(KafkaHelper, self).__init__(config=config)

            # Debug switch
            self.debug = True

            self._consumer = None
            self._producer = None
            self.result_topic = self.config['result_topic']
            self.error_log_topic = self.config["error_topic"]
            self.auto_offset_reset = self.config["auto_offset_reset"]

            self.listener_thread = None
        except Exception as e:
            print(e)

    def get_consumer(self):
        try:
            self._consumer = KafkaConsumer(
                self.config["input_topic"],  # topic name
                bootstrap_servers=self.config["bootstrap_servers"],
                auto_offset_reset=self.auto_offset_reset,
                group_id=self.config["consumer_group_id"],
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
            self.logger.info("Kafka Consumer is UP!")
        except Exception as e:
            self.logger.error("Kafka Consumer can not be started! The exception was: %s" % str(e))
            exit(1)

    def get_producer(self):
        try:
            self._producer = KafkaProducer(
                client_id=self.config["producer_group_id"],
                bootstrap_servers=self.config["bootstrap_servers"],
            )
            self.logger.info("Kafka Producer is UP!")
        except Exception as e:
            self.logger.error("Kafka Producer can not be started! The exception was: %s" % str(e))
            exit(1)

    def set_thread_manager(self, _thread_manager):
        self.listener_thread = _thread_manager

    def publish_message(self, key, value, topic):
        try:
            key_bytes = bytes(key, encoding='utf-8')
            value_bytes = bytes(value, encoding='utf-8')
            self._producer.send(topic, key=key_bytes, value=value_bytes)
            self._producer.flush()
            if self.debug:
                self.logger.info("Message published successfully. Key:%s, Value:%s" % (key, value))
        except Exception as ex:
            if self.debug:
                raise ex
            self.logger.info("Exception in publishing message. Key:%s, Value:%s" % (key, value))

    def listen_kafka(self):
        self.logger.info("I'm listening!")
        t = self.listener_thread(self, logger=self.logger, redis=self.redis, db_helper = self.db_helper)
        t.start()
