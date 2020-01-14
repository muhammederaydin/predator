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

import logging
import socket


class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def __init__(self, app_name, *args, **kwargs):
        self.appname = app_name
        super(ContextFilter, self).__init__(*args, **kwargs)

    def filter(self, record):
        record.appname = self.appname
        return True


class LogHelper:
    LOG_FORMAT = '[%(levelname)-5s] %(asctime)s.%(msecs)03d [%(process)d] %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, settings):
        if settings['log_file'] is None:
            log_file = 'log-file-not-configured.log'
        else:
            log_file = settings['log_file']

        logging.basicConfig(level=logging.DEBUG,
                            format=self.LOG_FORMAT,
                            datefmt=self.DATE_FORMAT)

        self.logger = logging.getLogger()

        ct = ContextFilter(settings.get('log_app_name', 'undefined-app'))

        self.logger.setLevel(logging.DEBUG)
        self.logger.addFilter(ct)

        file_logger_formatter = logging.Formatter(fmt=self.LOG_FORMAT, datefmt=self.DATE_FORMAT)

        file_logger_handler = logging.FileHandler(filename=log_file, encoding='utf8')
        file_logger_handler.setFormatter(file_logger_formatter)
        file_logger_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(file_logger_handler)

        for _logger in [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
            _logger.addFilter(ct)

    def get_logger(self):
        return self.logger
