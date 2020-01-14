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

import os
import argparse
from cryptography.fernet import Fernet
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Config Manager')

parser.add_argument("-c", "--create-security-config", help="Initialize empty database", action='store_true')
parser.add_argument("-ec", "--encrypt-config-file", help="Encrypt a config file", action='store_true')
parser.add_argument("-dc", "--decrypt-config-file", help="Decrypt a config file", action='store_true')
parser.add_argument("--config-file", type=str, help="Plain config file name")


args = parser.parse_args()


def create_security_config():
    _key = Fernet.generate_key()
    _salt = os.urandom(16)
    _identifier = b"crypted:"

    if os.path.exists(".sconf"):
        _ask = input("Config file exits, do you want to override? [yes/NO]: ")
        if _ask != "yes":
            print("No changes made! Current config file remains sane.")
            exit(0)

    with open(".sconf", "wb") as f:
        f.write(_key)
        f.write(_salt)
        f.write(_identifier)

    print("Security config created.")


def _read_security_config():
    try:
        with open(".sconf", "rb") as _f:
            _line = _f.read()
            _key = _line[0:44]
            _salt = _line[44:60]
            _identifier = _line[60:]

        return _key, _salt, _identifier

    except Exception as e:
        print(str(e))
        exit(1)


def encrypt_config_file(config_file):
        _config_dict = dict()
        _key, _salt, _identifier = _read_security_config()

        _parser = ConfigParser()
        _parser.read(config_file)

        _fernet = Fernet(_key)

        for _section_name in _parser.sections():
            for _item_name, _item_value in _parser.items(_section_name):
                _crypted_value =  _fernet.encrypt(bytes(_item_value, "utf-8"))
                _parser.set(_section_name, _item_name, (_identifier + _crypted_value).decode("utf-8"))

        _encrypted_file_name = config_file.replace(".plain", "")

        _parser.write(open(_encrypted_file_name, 'w'))


def decrypt_config_file(config_file):
    _config_dict = dict()
    _key, _salt, _identifier = _read_security_config()

    _parser = ConfigParser()
    _parser.read(config_file)

    _fernet = Fernet(_key)

    for _section_name in _parser.sections():
        for _item_name, _item_value in _parser.items(_section_name):
            _decrypted_value = _fernet.decrypt(_item_value[len(_identifier):].encode('utf8'))
            _parser.set(_section_name, _item_name, _decrypted_value.decode("utf8"))

    _decrypted_file_name = config_file.replace(".conf", ".conf.plain")

    _parser.write(open(_decrypted_file_name, 'w'))


if __name__ == '__main__':
    if args.create_security_config:
        create_security_config()

    if args.encrypt_config_file and args.config_file != "":
        encrypt_config_file(args.config_file)

    if args.decrypt_config_file and args.config_file != "":
        decrypt_config_file(args.config_file)
