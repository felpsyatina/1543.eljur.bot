import sys
from datetime import datetime
import config
import requests


def telegram_alert(module, log_line, tg_parse_mode = None):
	# Special bot will sent special alert to specified technical chat or resposible person
	# in telegram about "all crashed!"  
	# tg_parse_mode can be "HTML" or "Markdown"
	req = "https://api.telegram.org/bot" + config.secret["tg_technical"]["token"] + "/sendMessage?"
	if tg_parse_mode:
		req = req + "parse_mode=" + tg_parse_mode + "&"
	chat_id = config.secret["tg_technical"]["chats"].get(module, None)
	if not chat_id:
		chat_id = config.secret["tg_technical"]["default_chat"]
	req = req + "chat_id=" + str(chat_id) + "&text=" + log_line
	sys.stderr.write("Request: " + req +"\n")
	res = requests.get(req, verify=False)
	sys.stderr.write("Result code " + str(res.status_code) + "\n")


def save_log_file(module, log_line):
	filename = config.params["log_files"].get(module, None)
	if not filename:
		filename = config.params["log_files"]["default"]
	try:
		with open(filename, "a") as fout:
			fout.write(log_line)
	except Exception as err:
			sys.stderr.write("!!!!!!!!!!!!!!!! Cannot open log file " + filename + ": " + str(err) + "\n")
			sys.stderr.flush()



def log(module, log_line, add_time=True):
	if add_time:
		curtime = " at " + str(datetime.now())
	else:
		curtime = ""
	full_log_line = "**" + module + curtime + ": " + log_line + "\n"

	sys.stderr.write(full_log_line)
	sys.stderr.flush()

	if module[-9:] == "_critical":
		if config.params.get("send_technical_telegram_alerts", False):
			try:
				telegram_alert(module, full_log_line)
			except Exception as err:
				sys.stderr.write("!!!!!!!!!!!!!!!! Cannot send telegram alert: " + str(err) + "\n")
				sys.stderr.flush()
		else:
			sys.stderr.write("!!!!!!!!!!!!!!!! Technical critical alerts is switched off in config")
			sys.stderr.flush()

	if module[-5:] == "_save":
		if config.params.get("save_log_to_file", False):
			save_log_file(module, full_log_line)

