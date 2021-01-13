import requests
from lxml import etree
import execjs
import sys
import json
import time

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
		header = {
			  'Referer': 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/index.do',
              'Cookie': '_WEU=' + requests.utils.dict_from_cookiejar(cookie.cookies)['_WEU'] + '; MOD_AUTH_CAS=' + requests.utils.dict_from_cookiejar(self.session.cookies)['MOD_AUTH_CAS'] + ';'
			  }
		return header
	
	def get_info(self, headers):
		personal_info_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/getMyDailyReportDatas.do'
		
		info_response = self.session.post(personal_info_url, data={'rysflb': 'BKS', 'pageSize': '1', 'pageNumber': '1'}, headers=headers)
		return info_response
		
	def login(self, stuid, password):
		login_url = 'https://newids.seu.edu.cn/authserver/login'
	
		s = self.session	
		formdata = self.create_login_formdata(etree.HTML(s.get(login_url).text, parser=etree.HTMLParser()), 
										      stuid, 
										      password)
		s.post(login_url, data=formdata, allow_redirects=False)
		return s.post(login_url, data=formdata)
		
	def punchin(self):
		punchin_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'
		headers = self.create_header()
		info_response = self.get_info(headers)
		data = eval(info_response.text.replace("null", "None"))['datas']['getMyDailyReportDatas']['rows'][0]
		data['CREATED_AT'] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
		data['NEED_CHECKIN_DATE'] = time.strftime("%Y-%m-%d", time.localtime())
		data['DZ_JSDTCJTW'] = 36.3
		return self.session.post(punchin_url, headers=headers, data=data)
		
		
if __name__ == "__main__":
	report = Report()
	print("Login html")
	print(report.login(sys.argv[1], sys.argv[2]).text)
	
	s = report.punchin()
	print("Login html")
	print(s.text)
	
	
