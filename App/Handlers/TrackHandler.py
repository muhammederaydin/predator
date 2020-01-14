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

from .BaseHandler import BaseHandler
from urllib.parse import urlparse
from App.Core.utils import get_current_timestamp
from datetime import datetime


class Tracker(object):

    def __init__(self,  kafka, logger, redis, db_helper):

        self.data = None
        self.user = None
        self.path = None
        self.url = None
        self.source = None
        self.kafka = kafka
        self.logger = logger
        self.redis = redis
        self.db_helper = db_helper
        super(Tracker, self).__init__()

    def run(self, data):
        self.data = data # consumed message from kafka
        self.user = self.data.get("user_id")
        self.path = self.data.get("path_")
        self.url = self.data.get("url")
        # First Check Users Path, Update If It is Needed
        self.check_list()
        # Then Start Track
        _r_dict = self.tracker()
        return _r_dict

    def check_utm(self, url):
        """

        Check User URL for Detect If User Comes From Any Source

        url: user url

        """
        try:
            i = urlparse(url)
            a = i.query
            b = a.split("&")
            if len(b) >= 4:
                source = b[0].split("=")[1]
                self.logger.info("Utm Parse Complete !!!")
                return source
            else:
                return False
        except Exception as e:
            self.logger.error("Utm Source Parse Exception : %s" % str(e))
            raise e

    def check_list(self):
        """ 
        Check and Create Users Path List

        Check List Last Value, If It is Not Same or List Empty    
        Then It Should Append The List
        
        """
        try:
            list_lv = self.get_last_path(self.user)
            if list_lv == self.path:
                pass
            else:
                self.redis.insert_sequential(self.user, self.path)
                self.redis.set_key_expire(self.user, 30)
                self.logger.info("Path info Inserted to User's List")
        except Exception as e:
            self.logger.error("Check List Exception : %s" % str(e))
            raise e

    def get_last_path(self, list_name):
        """

        Get Users Paths List From Redis

        list_name: this parameter is a redis key which inserted paths for
        each user. This parameter should be user_id or any other unique value
        for users.

        """
        try:
            if self.redis.check_if_exist(list_name):
                _list = self.redis.get_list_key_last_value(list_name)
                return _list
            else:
                self.logger.info("List Doesn't Exist. Creating ...")
                # Create List

        except Exception as e:
            self.logger.error("Get List Exception : %s" % str(e))
            raise e

    def get_flows(self, flow_key):
        """

        Get Created Flows Which are Active

        flow_key: This parameter should be created flow name 

        """
        # get active flow for tracking
        active_flows = []
        current_ts = get_current_timestamp()
        try:
            _flows = self.redis.get_keys(flow_key)
            for _flow_key in _flows:
                splitted_flow = _flow_key.split('|')
                if len(splitted_flow) > 1:
                    # if time interval flow
                    time_portion = splitted_flow[-1]
                    start_time, end_time = map(int, time_portion.split(':'))
                    if start_time <= current_ts <= end_time:
                        active_flows.append(_flow_key)
                else:
                    active_flows.append(_flow_key)
            self.logger.info("Get Flows Complete !!!")
            return active_flows
        except Exception as e:
            self.logger.error("Get Flows Exception : %s" % str(e))
            raise e

    def get_user_paths(self, user):
        # get user movements
        """

        Get User Movements(Path journey)

        user: This parameter should be user_id, function return paths
        for user_id

        """
        try:
            _user_paths = self.redis.get_key_list_all_element(user)
            self.logger.info("Get User Paths Complete !!!")
            return _user_paths
        except Exception as e:
            self.logger.error("Get User Paths Exception : %s" % str(e))
            raise e

    # ["/","/urunler*Mail","/urunler/satin-alma*SMS__Mail__pop-up"]

    def action(self, action, user_info, utm_source=None):
        """

        This Function Detect Which Action Should Execute and Execute Action
        With Correct Function

        action: action name(must be sms, email, pop-up, alert)
        user_info: user info which execute info for
        utm_source: specify if user comes from any source else should take
        default parameter None

        """
        try:
            if "__" in action:
                action = action.split("__")[1]
            if utm_source is None:
                if action.lower() == "sms":
                    self.sms_action(user_info, utm_source)
                elif action.lower() == "email":
                    self.mail_action(user_info, utm_source)
                elif action.lower() == "pop-up":
                    self.pop_up_function(user_info, utm_source)
                elif action.lower() == "alert":
                    self.alert_function(user_info, utm_source)
                else:
                    self.logger.info("Can't Find Correct Action")
            else:
                if action.lower() == "sms" and utm_source == self.source:
                    self.sms_action(user_info, utm_source)
                elif action.lower() == "email" and utm_source == self.source:
                    self.mail_action(user_info, utm_source)
                elif action.lower() == "pop-up" and utm_source == self.source:
                    self.pop_up_function(user_info, utm_source)
                elif action.lower() == "alert" and utm_source == self.source:
                    self.alert_function(user_info, utm_source)
                else:
                    self.logger.info("Can't Find Correct Action")
                self.logger.info("Action is Done !!!")

        except Exception as e:
            self.logger.error("Action Exception : %s" % str(e))
            raise e
    
    def action_founder(self, flow, p_len, user_paths):
        """

        Function Seek for Action Without Specific Source Info
        This User Might Be Come Directly(Organic)

        """
        try:
            __flow = []
            for i in range(p_len):
                if "*" in str(flow[i]):
                    _splited_flow = _flow[i].split("*")
                    __flow.append(_splited_flow[0])
                    if user_paths[i] == _splited_flow[0]:
                        action = _splited_flow[1] if len(_splited_flow) >= 2 \
                                                    else False
                        if action:
                            self.action(action, user_info=self.user)
                    else:
                        self.logger.info("Cannot Find Match With Flow \
                                         and User Movement. Passed")
                else:
                    __flow.append(_flow[i])
                    if _user_p[i] != _flow[i]:
                        continue
                    self.logger.info("No Action Found. Continue.")
        except Exception as e:
            self.logger.error("Action Founder Error: {}".format(str(e)))
    
    def action_founder_with_source(self, flow, p_len, user_paths):
        """
    
        This Function Seek for Action With Specific Source
        Like search engine(google-yandex) or social media(facebook-twitter)

        """
        try:
            __flow = []
            for i in range(p_len):
                if "*" in str(flow[i]) and len(flow[i].split("*")) > 1:
                    _splited_flow = flow[i].split("*")
                    __flow.append(_splited_flow[0])
                    if str(user_paths[i]) == str(_splited_flow[0]):
                        source = _splited_flow[1].split("__")[0] if \
                            len(_splited_flow) > 1 else False
                        action = _splited_flow[1].split("__")[1] if \
                            len(_splited_flow) > 1 else False
                        if action:
                            self.action(action=action, user_info=self.user, 
                                        utm_source=source)
                        else:
                            self.logger.info("Cannot Find Match With Flow and \
                                             User Movement. Passed")
                    else:
                        __flow.append(_flow[i])
                        if _user_p[i] != _flow[i]:
                            continue
                        self.logger.info("No Action Found. Continue.")  
        except Exception as e:
            self.logger.error("Action Founder With Source Error: \
                              {}".format(str(e)))

    def tracker(self):
        self.source = self.check_utm(self.url)
        if self.source is False:
            # user tracking without source
            try:
                _user_p = self.get_user_paths(self.user)
                _flows = self.get_flows(flow_key="tracker_*")
                __flow = []
                for flow in _flows:
                    _flow = self.redis.get_key_list_all_element(flow)
                    _user_p_len = len(_user_p)
                    self.action_founder(_flow, _user_p_len, _user_p)
                    for i in range(_user_p_len):
                        if "*" in str(_flow[i]):
                            _splited_flow = _flow[i].split("*")
                            __flow.append(_splited_flow[0])
                            if _user_p[i] == _splited_flow[0]:
                                action = _splited_flow[1] if len(_splited_flow) >= 2 else False
                                if action:
                                    self.action(action, user_info=self.user)
                            else:
                                self.logger.info("Cannot Find Match With Flow and User Movement. Passed")

                        else:
                            __flow.append(_flow[i])
                            if _user_p[i] != _flow[i]:
                                continue
                            self.logger.info("No Action Found. Continue.")

                    if __flow == _user_p:
                        _dict = dict()
                        _dict["user_id"] = self.user
                        _dict["users_path"] = _user_p
                        _dict["flow"] = _flow
                        self.logger.info("Tracker Complete")

            except Exception as e:
                self.logger.error("Tracker Exception : %s" % str(e))
                raise e
        else:
            # user with UTM tracking
            try:
                self.logger.info("User with UTM Tracker Started ...")
                _user_p = self.get_user_paths(self.user)
                _flows = self.get_flows(flow_key="utm_tracker_*")
                __flow = []
                for flow in _flows:
                    _flow = self.redis.get_key_list_all_element(flow)
                    _user_p_len = len(_user_p)
                    self.action_founder_with_source(_flow, _user_p_len,
                                                    _user_p)
                    for i in range(_user_p_len):
                        try:
                            if "*" in str(_flow[i]) and len(_flow[i].split("*")) > 1:
                                _splited_flow = _flow[i].split("*")
                                __flow.append(_splited_flow[0])
                                if str(_user_p[i]) == str(_splited_flow[0]):
                                    source = _splited_flow[1].split("__")[0] if len(_splited_flow) > 1 else False
                                    action = _splited_flow[1].split("__")[1] if len(_splited_flow) > 1 else False
                                    if action:
                                        self.action(action=action, user_info=self.user, utm_source=source)
                                else:
                                    self.logger.info("Cannot Find Match With Flow and User Movement. Passed")

                            else:
                                __flow.append(_flow[i])
                                if _user_p[i] != _flow[i]:
                                    continue
                                self.logger.info("No Action Found. Continue.")

                        except Exception as e:
                            self.logger.error(e)
                    if __flow == _user_p:
                        _dict = dict()
                        _dict["user_id"] = self.user
                        _dict["users_path"] = _user_p
                        _dict["flow"] = _flow
                        self.logger.info("UTM User Tracker Complete")

            except Exception as e:
                self.logger.error("UTM User Tracker Exception : %s" % str(e))
                raise e

    def check_action(self, user_id, action):
        """

        Check Action Execution Time. If Already Executed Then Return False
        Else Set Expire Time Executed Action
        
        """
        try:
            _key = str(user_id) + "_" + str(action)
            if self.redis.check_if_exist(_key):
                self.logger.info("Action Has Already Executed")
                return False
            else:
                self.redis.set_key_value(_key, "0")
                self.redis.set_key_expire(_key, 300)
                return True
        except Exception as e:
            raise e

    def sms_action(self, user_info, utm_source):
        # Send SMS Function

        try:
            action = "sms"
            if self.check_action(user_info, "sms"):
                _to_mongo = {"user": user_info, "utm_source": utm_source, 
                             "action": action, "path": self.path,
                             "time": datetime.now()}
                self.db_helper.insert_to_mongo(collection="action", 
                                               data=_to_mongo)
                self.logger.info("Predator Detect SMS Action and Execute It")
        except Exception as e:
            raise e

    def mail_action(self, user_info, utm_source):
        # Send Mail Function
        try:
            action = "email"
            if self.check_action(user_info, "email"):
                _to_mongo = {"user": user_info, "utm_source": utm_source, 
                             "action": action, "path": self.path,
                             "time": datetime.now()}
                self.db_helper.insert_to_mongo(collection="action", 
                                               data=_to_mongo)
                self.logger.info("Predator Detect Mail Action and Execute It")
        except Exception as e:
            raise e

    def pop_up_function(self, user_info, utm_source):
        # Pop-up Function
        try:
            action = "pop-up"
            if self.check_action(user_info, "pop-up"):
                _to_mongo = {"user": user_info, "utm_source": utm_source, 
                             "action": action, "path": self.path,
                             "time": datetime.now()}
                self.db_helper.insert_to_mongo(collection="action", 
                                               data=_to_mongo)
                self.logger.info("Predator Detect Pop-up Action and Execute It")
        except Exception as e:
            raise e

    def alert_function(self, user_info, utm_source):
        # Pop-up Function
        try:
            action = "alert"
            if self.check_action(user_info, "alert"):
                _to_mongo = {"user": user_info, "utm_source": utm_source, 
                             "action": action, "path": self.path,
                             "time": datetime.now()}
                self.db_helper.insert_to_mongo(collection="action", 
                                               data=_to_mongo)
                self.logger.info("Predator Detect Alert Action and Execute It")
        except Exception as e:
            raise e

