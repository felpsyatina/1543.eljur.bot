import sys
from datetime import datetime


def telegram_alert(module, log_line):
	# Special bot will sent special alert to specified technical chat or resposible person
	# in telegram abot "all crashed!" and log_line 
	pass


def log(module, log_line, add_time=True):
	if add_time:
		curtime = " at " + str(datetime.now())
	else:
		curtime = ""
	full_log_line = "**" + module + curtime + ": " + log_line + "\n"

	sys.stderr.write(full_log_line)

	if module[-9:] == "_critical":
		try:
			telegram_alert(module, full_log_line)
		except Exception as err:
			sys.stderr.write("!!!!!!!!!!!!!!!! Cannot send telegram alert: " + str(s) + "\n")

