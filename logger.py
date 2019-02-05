import sys

def telegram_alert(module, log_line):
	# Special bot will sent special alert to specified technical chat or resposible person
	# in telegram abot "all crashed!" and log_line 
	pass

def log(module, log_line):
	sys.stderr.write("**" + module + ": " + log_line + "\n")
	if module[-9:] == "_critical":
		try:
			telegram_alert(module, log_line)
		except Exception as err:
			sys.stderr.write("!!!!!!!!!!!!!!!! Cannot send telegram alert: " + str(s) + "\n")

