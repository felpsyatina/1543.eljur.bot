# -*- coding: utf-8 -*-
import json
import os

cur_path = os.path.dirname(os.path.abspath(__file__))

secrets_config_file = cur_path + "/configs/config_secrets.json"
global_config_file = cur_path + "/configs/config.json"
db_copies_path = cur_path + "/db_copies"


def load_config(filename):
    with open(filename, "r", encoding="utf-8") as configfile:
        res = json.loads(configfile.read())
        return res


params = load_config(global_config_file)
secret = load_config(cur_path + "/" + params["config_secret_path"])
