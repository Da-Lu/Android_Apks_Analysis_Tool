#!/usr/bin/env
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os, io, json

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

#[node['name'].rfind('.') + 1:]