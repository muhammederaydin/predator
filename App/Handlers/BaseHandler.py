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

import json
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        self._input = None
        super(BaseHandler, self).__init__(*args, **kwargs)

    @property
    def settings(self):
        return self.application.settings

    @property
    def db(self):
        return self.application.db

    @property
    def logger(self):
        return self.application.logger

    @property
    def redis(self):
        return self.application.redis

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset="utf-8"')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'x-current-member, '
                        + 'x-requested-with, '
                        + 'Accept, Content-Type, '
                        + 'Authorization, '
                        + 'Access-Control-Allow-Origin, '
                        + 'Access-Control-Max-Age, '
                        + 'Access-Control-Allow-Credentials')

        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE, PUT')

    def write_response(self, status=200, message="", response_status="error"):
        self.set_status(status_code=status)
        self.finish({
            "status": response_status,
            "message": message
        })
