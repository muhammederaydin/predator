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
from .Handlers.TrackHandler import Tracker


class Predator(threading.Thread):
    daemon = True

    def __init__(self, kafka, logger, redis, db_helper):

        try:
            self.kafka = kafka
            self.kafka.get_consumer()
            self.kafka.get_producer()
            self.debug = True
            self.logger = logger
            self.redis = redis
            self.db_helper = db_helper
            self.logger.info("Predator Engine Execution is Done !!!")
        except Exception as e:
            self.logger.error("Predator Engine Execution Error : %s" % str(e))
        super(Predator, self).__init__()

    def run(self):
        for message in self.kafka._consumer:
            message = list(message)[6][0]
            if self.debug:
                print(message)
            try:
                _tracked = Tracker(kafka=self.kafka, logger=self.logger, redis=self.redis,
                                       db_helper=self.db_helper).run(message)
                self.logger.info("Predator Tracker Complete")
                if _tracked is None or False:
                    self.logger.info("User Did Not Tracked")
                    pass
                else:
                    #self.kafka.publish_message("Tracked", _tracked, 
                    #self.kafka.result_topic)
                    self.logger.info("Predator Tracked a User")
            except Exception as e:
                # Send message to another Kafka topic
                self.logger.error("Run Exception : %s" % str(e))
                print(str(e))
