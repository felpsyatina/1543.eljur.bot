# -*- coding: utf-8 -*-
import json
import os

cur_path = os.path.dirname(os.path.abspath(__file__))

secrets_config_file = cur_path + "/configs/config_secrets.json"
global_config_file = cur_path + "/configs/config.json"


def load_config(filename):
	configfile = open(filename, "r", encoding="utf-8")
	jsonstring = configfile.read()
	res = json.loads(jsonstring)
	configfile.close()
	return res


params = load_config(global_config_file)
secret = load_config(cur_path + "/" + params["config_secret_path"])
