import json
import datetime
import pytz 
import random

def load_formdata(filename):
	data = json.load(open(filename, encoding='utf-8'))
	data['CREATED_AT'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M")
	data['DZ_DBRQ'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M")
	data['NEED_CHECKIN_DATE'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d")
	data['CZRQ'] = data['DZ_DBRQ'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
	
	data['DZ_JSDTCJTW'] = 36 + 0.1*random.randint(0,10)
	return data

if __name__ == "__main__":
	formdata = load_formdata("formdata.json")
	print(formdata)