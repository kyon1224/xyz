import sys
import requests
from lxml import etree
import execjs
import load_data
from requests.exceptions import ConnectionError


class Report:

	def __init__(self):
		self.session = requests.Session()

	def create_login_formdata(self, html, sduid, password):
		lt = html.xpath('//*[@id="casLoginForm"]/input[1]/@value')[0]
		dllt = html.xpath('//*[@id="casLoginForm"]/input[2]/@value')[0]
		execution = html.xpath('//*[@id="casLoginForm"]/input[3]/@value')[0]
		_eventId = html.xpath('//*[@id="casLoginForm"]/input[4]/@value')[0]
		rmShown = html.xpath('//*[@id="casLoginForm"]/input[5]/@value')[0]
		pwdDefaultEncryptSalt = html.xpath('//*[@id="casLoginForm"]/input[6]/@value')[0]
		return {
			'username': sduid,
			'password': self.encrypt_password(password, pwdDefaultEncryptSalt),
			'lt': lt,
			'dllt': dllt,
			'execution': execution,
			'_eventId': _eventId,
			'rmShown': rmShown
			}

	def encrypt_password(self, password, salt):
		with open('encrypt.js', 'r') as f:
			js = f.read()
			ctx = execjs.compile(js)
			password = ctx.call('encryptAES', password, salt)
		return password

	def create_header(self):
		cookie_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/configSet/noraml/getRouteConfig.do'
		cookie = self.session.get(cookie_url)


	def get_info(self, headers):
		personal_info_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/getMyDailyReportDatas.do'

		info_response = self.session.post(personal_info_url, data={'rysflb': 'BKS', 'pageSize': '1', 'pageNumber': '1'}, headers=headers)
		return info_response

	def create_formdata(self, json_filename):
		userinfo_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/api/base/getUserDetailDB.do'

		formdata = load_data.load_formdata(json_filename)
		userinfo = self.session.get(userinfo_url).json()['data']
		formdata['USER_NAME'] = userinfo['USER_NAME']
		formdata['DEPT_NAME'] = userinfo['DEPT_NAME']
		return formdata

	def login(self, stuid, password):
		login_url = 'https://newids.seu.edu.cn/authserver/login'

		s = self.session
		formdata = self.create_login_formdata(
			etree.HTML(s.get(login_url).text, parser=etree.HTMLParser()),
			stuid,
			password)
		s.post(login_url, data=formdata, allow_redirects=False)
		return s.post(login_url, data=formdata)

	def punchin(self, json_filename):
		punchin_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'

		self.create_header()
		# info_response = self.get_info(headers)
		return self.session.post(punchin_url, data=self.create_formdata(json_filename))

	def get_session(self):
		return self.session


if __name__ == "__main__":
	report = Report()
	retry_counter = 5
	while retry_counter > 0:
		try:
			login_response = report.login(sys.argv[1], sys.argv[2])
		except ConnectionError:
			continue
		break
	try:
		assert "退出" in login_response.text, "Invalid password or studentID"
	except NameError:
		raise ConnectionError('Retry 5 times but still fail to log-in.')

	print("Login success")
	print("==============================")

	retry_counter = 5
	while retry_counter > 0:
		try:
			punchin_response = report.punchin(sys.argv[3])
		except ConnectionError:
			continue
		break
	try:
		print(punchin_response.text)
	except NameError:
		raise ConnectionError('Retry 5 times but still fail to punch-in.')


