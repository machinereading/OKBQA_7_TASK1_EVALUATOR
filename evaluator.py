# -*- coding: utf-8 -*-
import os
import time
from bottle import route, run, template, post, request, response
import urllib
import urllib2
import json
import codecs
import collections
import socket
from collections import OrderedDict

data_disambi_en = {}
data_redir_en = {}
edbr = "http://dbpedia.org/resource/"

def tree(): return collections.defaultdict(tree)

def file_reader():
    print('dis start')
    f = open('data/disambiguations_en.ttl', 'r')
    lines = f.readlines()
    temp = set()
    for row in lines:
        spt = row.strip().split(' ')
        s = spt[0].replace(edbr,"").replace('<','').replace('>','')
        o = spt[2].replace(edbr, "").replace('<', '').replace('>', '')
        if o in data_disambi_en:
            temp = data_disambi_en[o]
            temp.add(s)
#            print(data_disambi_en[o])
#            print(s)
#            print(o)
            pass
        else:
            data_disambi_en[o] = set([s])
    print('dis end')
    print('rediec start')
    f = open('data/redirects_en.ttl', 'r')
    lines = f.readlines()
    temp = set()
    for row in lines:
        spt = row.strip().split(' ')
        s = spt[0].replace(edbr,"").replace('<','').replace('>','').replace('_','')
        o = spt[2].replace(edbr, "").replace('<', '').replace('>', '').replace('_','')
        if s in data_redir_en:
            temp = data_redir_en[s]
            temp.add(s)
            pass
        elif o in data_redir_en:
            temp = data_redir_en[o]
            temp.add(s)
            pass
        else:
            data_redir_en[s] = set([o])
            data_redir_en[o] = set([s])
    print('rediec end')

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

def add_info(q_info):
	tmp_dict = OrderedDict()
	tmp_dict['id'] = q_info['id']
	tmp_dict['question'] = q_info['question']
	return tmp_dict

def add_false_negative_answer(data, sys, q_info, n) :
	tmp_dict = OrderedDict()
	tmp_dict['id'] = q_info['id']
	tmp_dict['question'] = q_info['question']
	tmp_dict['true_positives'] = list(data & sys)
	tmp_false_negatives = []
	tmp_false_negatives = list(data - sys)
	tmp_list = []
	if len(tmp_false_negatives) > n:
		for i in range(n):
			tmp_list.append(tmp_false_negatives[i])
	else:
		tmp_list = tmp_false_negatives
	tmp_dict['false_negatives_up_to_n'] = tmp_list
	tmp_dict['false_negatives_number'] = len(tmp_false_negatives)
	return tmp_dict

def add_false_positive_answer(data, sys, q_info, n) :
	tmp_dict = OrderedDict()
	tmp_dict['id'] = q_info['id']
	tmp_dict['question'] = q_info['question']
	tmp_dict['true_positives'] = list(data & sys)
	tmp_false_positives = []
	tmp_false_positives = list(sys - data)
	tmp_list = []
	if len(tmp_false_positives) > n:
		for i in range(n):
			tmp_list.append(tmp_false_positives[i])
	else:
		tmp_list = tmp_false_positives
	tmp_dict['false_positives_up_to_n'] = tmp_list
	tmp_dict['false_positives_number'] = len(tmp_false_positives)
	return tmp_dict

@route('/evaluation', method=['OPTIONS', 'POST'])
@enable_cors
def evaluate() :
	correct = 0.0

	input_data = request.body.read()
	#print data
	# load questions & language
	input_json = json.loads(input_data)
	lang = input_json['language']
	conf = OrderedDict()
	try :
		conf['KB'] = input_json['config']['address']['KB']
	except :
		print 'using default kb'
	try :
		conf['DM'] = input_json['config']['address']['DM']
	except :
		print 'using default dm'
	try :
		conf['TGM'] = input_json['config']['address']['TGM']
	except :
		print 'using default tgm'
	try :
		conf['QGM'] = input_json['config']['address']['QGM']
	except :
		print 'using default qgm'
	try :
		conf['AGM'] = input_json['config']['address']['AGM']
	except :
		print 'using default agm'
	try :
		conf['timelimit'] = int(input_json['config']['timelimit'])
	except :
		print 'using default timelimit'
		conf['timelimit'] = int(120)
	try :
		conf['N'] = int(input_json['config']['n'])
	except :
		print 'using default n'
		conf['N'] = int(10)

	if (('data' in input_json) and (len(input_json['data']) != 0)):
		questions = input_json['data']
	elif 'data_url' in input_json:
		data_file = input_json['data_url']
		f = send_getrequest(data_file)
		questions = json.loads(f)
	else:
		print 'using default dataset'
		data_file = "http://ws.okbqa.org/down/sample2.json"
		f = send_getrequest(data_file)
		questions = json.loads(f)

	output_json = OrderedDict()
	output_json['config'] = conf
	output_json['result'] = OrderedDict()

	correct_answer = []
	partial_answer = []
	false_negative_answer = []
	false_positive_answer = []
	failure = []
	time_out = []

	start_time = time.strftime("%y-%m-%d %H:%M:%S")
	output_json['result']['timestamp'] = start_time
	time_lapsed_start = time.time()

	for question in questions :
		if lang == question['lang'] :
			data = tree()
			data['input']['language'] = lang
			data['input']['string'] = question['question']
			data['conf']['address'] = conf
			data['conf']['sequence'] = input_json['config']['sequence']
			data['conf']['sync'] = 'on'
			print question['question']
			result = send_postrequest("http://ws.okbqa.org:7047/cm", json.dumps(data), conf['timelimit'])
			if result is None:
				time_out.append(add_info(question))
			else:
				tmp_log = json.loads(result)['log']
				for log in tmp_log:
					if '2. elapsed_time' in log:
						print(log['1. module'] + ' : ' + str(log['2. elapsed_time']))
					else:
						pass
				answers_sys = set()
				tmp_result = json.loads(result)['result']
				if tmp_result == []:
					failure.append(add_info(question))
				else:
					for ans in tmp_result:
						answers_sys.add(ans['answer'])
					answers_dataset = set(question['answer'])
					if answers_sys == answers_dataset:
						correct_answer.append(add_info(question))
					else:
						if len(answers_sys & answers_dataset) > 0:
							partial_answer.append(add_info(question))
						else:
							pass
						if len(answers_sys - answers_dataset) > 0:
							false_positive_answer.append(add_false_positive_answer(answers_dataset, answers_sys, question, conf['N']))
						else:
							pass
						if len(answers_dataset - answers_sys) > 0:
							false_negative_answer.append(add_false_negative_answer(answers_dataset, answers_sys, question, conf['N']))
						else:
							pass
		else:
			pass
	
	output_json['config']['sequence'] = input_json['config']['sequence']
	time_lapsed = time.time() - time_lapsed_start
	output_json['result']['time_lapsed'] = time_lapsed
	output_json['result']['correct_answer'] = correct_answer
	output_json['result']['partial_answer'] = partial_answer
	output_json['result']['false_negative_answer'] = false_negative_answer
	output_json['result']['false_positive_answer'] = false_positive_answer
	output_json['result']['failure'] = failure
	output_json['result']['time_out'] = time_out
	output_json['result']['correct_answer_rate'] = float(len(correct_answer)) / float(len(questions))
	output_json['result']['partial_answer_rate'] = float(len(partial_answer)) / float(len(questions))
	output_json['result']['false_negative_answer_rate'] = float(len(false_negative_answer)) / float(len(questions))
	output_json['result']['false_positive_answer_rate'] = float(len(false_positive_answer)) / float(len(questions))
	output_json['result']['failure_rate'] = float(len(failure)) / float(len(questions))
	output_json['result']['time_out_rate'] = float(len(time_out)) / float(len(questions))

	return json.dumps(output_json, indent=4)
#	print input_json
#	doc_type = input_json['type']

def send_getrequest(url):

	request = urllib2.Request(url, None, {'Content-Type':'application/x-www-form-urlencoded; charset=utf-8'})
	response = urllib2.urlopen(request)
	data = response.read()

	response.close()
	return data.replace('\xef\xbb\xbf','')

def send_postrequest(url, input_string, time_limit):
	try:
		req = urllib2.Request(url, data=input_string.encode('utf-8'), headers={'Content-Type':'application/x-www-form-urlencoded; charset=utf-8'})
		f = urllib2.urlopen(req, timeout=time_limit)
		data = f.read()
		return data.replace('\xef\xbb\xbf','')
	except socket.timeout, e:
		print('%r' % e)
		return None

if __name__ == "__main__":
    #file_reader()
	run(server='cherrypy', host='localhost', port=31999, debug=True)
    #run(server='cherrypy', host='110.45.238.116', port=31999, debug=True)
#run(host='121.254.173.77', port=31999, debug=True)
