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

from tornado.options import options, define
from App.Core import LogHelper, MongoDBHelper, RedisHelper, ConfigHelper
from tornado import web, ioloop
from App.Core import KafkaHelper
from App.Engine import Predator


define('LOG_FILE', type=str)

define('DB_ADDRESS', type=str, default='0.0.0.0')
define('DB_PORT', type=int, default=27017)
define('REDIS_HOST', type=str, default='0.0.0.0')
define('REDIS_PORT', type=int, default=6379)


class Engine(web.Application):
    redis = None
    logger = None
    connection = None
    engine = None
    kafka = None
    db = None
    db_helper = None


class Server:
    name = "Predator - User Tracking Engine"

    def __init__(self, host, port, config_file='app.conf'):
        self.env = 'LOCAL'
        self.host = host
        self.port = port
        self.config_file = config_file

        self.connection = None
        self.redis = None
        self.logger = None

        self._options = None

        self.app = Engine(**self.settings)

        # Logger
        try:
            self.app.logger = LogHelper.LogHelper(self.settings["app"])\
                                                    .get_logger()
        except Exception as e:
            print("Logger instance could not be initialized. \
                  Server will exit: {}".format(str(e)))
            exit(1)

        # MongoDB
        try:
            self.app.db_helper = MongoDBHelper(config=self.settings["mongodb"])
            self.app.db_connection = self.app.db_helper.get_connection()
        except Exception as e:
            self.app.logger.critical("MongoDB Connection Error:\
                                     {}".format(str(e)))

        # Redis Connection
        try:
            self.app.redis = RedisHelper(self.settings["redis"], 
                                         self.app.logger)
        except Exception as e:
            self.app.logger.critical("Redis could not be initialized. \
                                     Server will exit: {}".format(str(e)))
            exit(2)

        # Kafka
        try:
            self.app.kafka = KafkaHelper(self.settings["kafka"], 
                                         self.app.logger, self.app.redis, 
                                         self.app.db_helper)
        except Exception as e:
            self.app.logger.critical("Kafka consumer could not be initialized.\
                                     Server will exit: {}".format(str(e)))
            exit(2)

    @property
    def settings(self):
        if self._options is None:
            self._options = dict()
            try:
                self._options = ConfigHelper(self.config_file).get_config()

                if self.host is not None:
                    self._options['host'] = self.host

                if self.port is not None:
                    self._options['port'] = self.port

            except Exception as e:
                print("Config file could not be loaded! Server will exit.\
                      Error: {}".format(str(e)))
                exit(1)

        return self._options

    def start(self):
        self.app.listen(self.settings["app"]["port"])
        self.app.logger.info('Starting {} on port {}.'.format(self.name, 
                                                self.settings["app"]["port"]))
        self.app._ioloop = ioloop.IOLoop.current()

        # Add Thread mangage
        self.app.kafka.get_consumer()
        self.app.kafka.set_thread_manager(Predator)
        self.app._ioloop.add_callback(self.app.kafka.listen_kafka)

        self.app._ioloop.start()

    def stop(self):
        self.app._ioloop.stop()
        self.app.logger.info('Stopping server: CTRL+C')

