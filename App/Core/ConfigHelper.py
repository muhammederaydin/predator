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

from cryptography.fernet import Fernet
from configparser import ConfigParser
from configparser import MissingSectionHeaderError


class ConfigHelper(object):
    def __init__(self, config_file):
        _parser = ConfigParser()
        self.encrypt_identifier = None
        self._config_dict = dict()

        try:
            with open(".sconf", "rb") as _f:
                _line = _f.read()
                _key = _line[0:44]
                _salt = _line[44:60]
                _identifier = _line[60:]

            self.encrypt_identifier = _identifier.decode("utf-8")

            self.fernet = Fernet(_key)
        except Exception as e:
            print(str(e))
            raise Exception("Error while crypt engine initialization")

        try:
            _parser.read(config_file)
        except MissingSectionHeaderError:
            _parser.read_file(self.add_section_header(open(config_file), 'default'), source=config_file)
        except Exception as ex:
            raise Exception("Config file is not found.")

        try:
            for _section_name in _parser.sections():
                self._config_dict[_section_name] = dict()
                _section_dict = dict(_parser.items(_section_name))
                for _item_name in _section_dict:
                    _item_value = _section_dict[_item_name]
                    if _item_value.startswith(self.encrypt_identifier):
                        _item_value = self.decrypt(_item_value)

                    if _item_value == "True":
                        _item_value = True

                    if _item_value == "False":
                        _item_value = False

                    self._config_dict[_section_name][_item_name] = _item_value

        except Exception as e:
            raise Exception("Error while creating config dictionary")

    def get_config(self):
        return self._config_dict

    def decrypt(self, val):
        return self.fernet.decrypt(val[len(self.encrypt_identifier):].encode("utf-8")).decode("utf-8")

    def add_section_header(self, properties_file, header_name):
        yield '[{}]\n'.format(header_name)
        for line in properties_file:
            yield line
