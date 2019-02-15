import sys
sys.path.append("../..")

import logger
import config
import json
import time
import requests

STATE_FILE_NAME = config.params.get("github_commit_bot_state_file", "saved_state.txt")
SLEEP_TIME = config.params.get("github_commit_bot_sleep_time", 5*60)

monitoring_list = [
	{
		"name": "total",
		"url": "https://api.github.com/repos/IfelpsI/1543.eljur.bot/commits",
		"header": "",
	},
	{
		"name": "config_secrets",
		"url": "https://api.github.com/repos/IfelpsI/1543.eljur.bot/commits?path=/configs/config_secrets.json",
		"header": "<b>Alarm! config_secrets.json</b> has new commit(s)\n"
	}
]

def loading_saved_state():
	try:
		fin = open(STATE_FILE_NAME)
		res = json.loads(fin.read())
		fin.close()
		logger.log("github_commits_bot", "Previous state read from file complete")
		return res
	except Exception as err:
		logger.log("github_commits_bot", "File with previous state (" + STATE_FILE_NAME + ") not found or error when parsing state")
		return {}

def saving_current_state(cur_state):
	fout = open(STATE_FILE_NAME, "w")
	fout.write(json.dumps(cur_state))
	fout.close()

def get_info_from_github(url):
	res = requests.get(url)
	if res.status_code != 200:
		logger.log("github_commits_bot", "Github api returns " + str(res.status_code) + " code")
	return res.json()

def html_quote(strline):
	res = ""
	for symb in strline:
		if symb == "<":
			res += "&lt;"
		elif symb == ">":
			res += "&gt;"
		elif symb == "&":
			res += "&amp;"
		else:
			res += symb
	return res

def update_cur_state_and_create_alert(cur_state, new_state, cur_name, header = ""):
	msg = []
	for commit in new_state[::-1]:
		if commit["sha"] in cur_state:
			continue
		cur_state.append(commit["sha"])
		msg.append("<b>" + html_quote(commit["commit"]["author"]["name"]) + "</b>: " + html_quote(commit["commit"]["message"]))
	if len(msg) > 0:
		if len(msg) > 5:
			msg_line = str(len(msg)) + " new commits, last 5:\n"
		elif len(msg) > 1:
			msg_line = str(len(msg)) + " new commits:\n"
		else:
			msg_line = "New commit:\n"
		msg_line = header + msg_line + "\n".join(msg[-5:])
		logger.log("github_commits_bot","Sending message:\n" + msg_line)
		logger.telegram_alert("github_commits_bot_info", msg_line, tg_parse_mode="HTML")
	else:
		logger.log("github_commits_bot",cur_name + ": no new commits")
	return cur_state[-50:]




def main_loop(cur_state):
	while True:
		try:
			for cur_path in monitoring_list:
				new_state = get_info_from_github(cur_path["url"])
				cur_state[cur_path["name"]] = update_cur_state_and_create_alert(cur_state.get(cur_path["name"], []), 
					new_state,
					cur_path["name"], 
					header=cur_path["header"])
			saving_current_state(cur_state)
		except Exception as err:
			logger.log("github_commits_bot", "Error in main loop: " + str(err))
		time.sleep(SLEEP_TIME)






if __name__ == '__main__':

	main_loop(loading_saved_state())
