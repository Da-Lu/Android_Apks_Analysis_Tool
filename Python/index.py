#!/usr/bin/env python2

# Turn on debug mode.
from bs4 import BeautifulSoup
import io, json
import os, sys, stat, cgi, cgitb
cgitb.enable()

apps_base = "../../covert_dist/app_repo/bundle"
covert_base = "../../covert_dist"

def generateJson():
	L, result_list = [], []
	group_name = []
	result= {}
	#for filename in os.listdir(os.getcwd()):
	for filename in os.listdir('/var/www/html/covert_dist/app_repo/bundle/analysis/merged'):
		if filename.endswith('.xml'):
			group_name.append(filename[:filename.rfind('.')])
			L.append(BeautifulSoup(open(filename), 'lxml'))
	for i, soup in enumerate(L):
		data = {}
		data['application_name'] = group_name[i]
		data['component'] = []
		data['intent'] = []
		data['permission'] = []
		
		#component
		for component in soup.find_all('component'):
			new_component = {}
			#requiredpermissions
			if component.requiredpermissions != None:
				if component.requiredpermissions.get_text().encode('UTF-8').strip('\n') != '':
					new_component['RequiredPermissions'] = component.requiredpermissions.get_text().encode('UTF-8').strip('\n')
			#name
			if component.find('name') != None:
				if component.find('name').get_text().encode('UTF-8').strip('\n') != '':
					new_component['name'] = component.find('name').get_text().encode('UTF-8').strip('\n')
			#filter_action
			new_filter = []
			if component.intentfilter != None:
				for filter in component.intentfilter.find_all('filter'):
					if component.intentfilter.filter != None:
						for action in filter.find_all('actions'):
							if action != None:
								if action.get_text().encode('UTF-8').strip('\n') != '':
									new_filter.append({'action': action.get_text().encode('UTF-8').strip('\n')})
			if new_filter != []:
				new_component['filter'] = new_filter

			if new_component != {}:
				data['component'].append(new_component)
		
		#permission
		for permission in soup.find_all('permission'):
			if permission != None and permission.get_text().encode('UTF-8').strip('\n') != '' and permission.parent.name == 'actuallyusespermissions':
				data['permission'].append({'Permission': permission.get_text().encode('UTF-8').strip('\n')})
		#new_intent
		for intent in soup.find_all('intent'):
			new_intent = {}
			if intent.sender != None:
				if intent.sender.get_text().encode('UTF-8').strip('\n') != '':
					new_intent['sender'] = intent.sender.get_text().encode('UTF-8').strip('\n')
			if intent.action != None:
				new_intent['action'] = intent.action.get_text().encode('UTF-8').strip('\n').strip('\"')
			if intent.consumermethod != None:
				if intent.consumermethod.get_text().encode('UTF-8').strip('\n') != '':
					new_intent['consumermethod'] = intent.consumermethod.get_text().encode('UTF-8').strip('\n')
			if new_intent != {}:
				data['intent'].append(new_intent)

		result_list.append(data)
	result['result'] = result_list

	output = {}
	nodes, links = [], []
	index = 0
	for app in result_list:
		for node in app['component']:
			new_node = {}
			new_node['name'] = node['name']
			new_node['group'] = index
			if 'RequiredPermissions' in node:
				new_node['permission'] = node['RequiredPermissions']
			if 'filter' in node:
				new_node['filter'] = node['filter']
			new_node['groupName'] = app['application_name']
			nodes.append(new_node)
		index += 1
	output['nodes'] = nodes
	for app in result_list:
		for intent in app['intent']:
			new_intent2 = {}
			if intent['action'] != '':
				if next((i for i,x in enumerate(nodes) if intent['sender'] in x['name']), None) != None:
					new_intent2['source'] = next((i for i,x in enumerate(nodes) if intent['sender'] in x['name']), None)
				new_intent2['name'] = intent['action']
				new_intent2['color'] = 1
				for i, x in enumerate(nodes):
					if 'filter' in x:
						for action in x['filter']:
							if intent['action'] == action['action']:
								new_intent2['target'] = i
								if 'source' in new_intent2:
									links.append(new_intent2)
	seen = set()
	new_links = []
	for d in links:
		t = tuple(d.items())
		if t not in seen:
			seen.add(t)
			new_links.append(d)
	output['links'] = new_links
	with open('data.json', 'w') as f:
		json.dump(output, f)

def JsonTop():
	print("""Content-Type: application/json\n\n
		""")

def htmlTop():
	print("""Content-Type: text/html\n\n
	<!DOCTYPE html>
	<html lang="en">
		<head>
			<meta charset="utf-8"/>
			<title>Android Apks Analysis Tool</title>
		</head>
		<body>""")

def htmlTail():
	print("""
		</body>
	</html>
		""")

def writeFile(upload_dir, fileitem):
	if not fileitem.file: return
	fout = open (os.path.join(upload_dir, fileitem.filename), 'wb')
	while 1:
		chunk = fileitem.file.read(100000)
		if not chunk: break
		fout.write (chunk)
	fout.close()
	os.chmod(os.path.join(upload_dir, fileitem.filename), 0o777)

def save_uploaded_file (form_field, upload_dir):
	"""This saves a file uploaded by an HTML form.
		The form_field is the name of the file input field from the form.
		For example, the following form_field would be "file_1":
			<input name="file_1" type="file">
		The upload_dir is the directory where the file will be written.
		If no file was uploaded or if the field does not exist then
		this does nothing.
	"""
	form = cgi.FieldStorage()
	if form_field not in form: return
	fileitems = form[form_field]
	if type(fileitems) is not list:
		writeFile(upload_dir, fileitems)
	else:
		for fileitem in fileitems:
			writeFile(upload_dir, fileitem)

#main program
if __name__ == "__main__" :
	try:
		JsonTop()
		#store apks in apps folder
		save_uploaded_file("apks[]", apps_base)
		#using Tools to analysis apks
		import subprocess
		os.chdir(covert_base)
		FNULL = open('./log.txt', 'wb')
		process = subprocess.Popen(["sh", "./covert.sh", "bundle"], cwd="/var/www/html/covert_dist", stdout=FNULL, stderr=subprocess.STDOUT)
		process.wait()		
		#convert output to JSON format
		generateJson()
		#send JSON to Front End
		print("{\"ack\":\"ok\"}")
		# if true:
		# else :
	except:
		cgi.print_exception()