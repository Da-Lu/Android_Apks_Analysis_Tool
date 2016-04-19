#!/usr/bin/env python3

# Turn on debug mode.
import os, sys, stat, cgi, cgitb
cgitb.enable()

apps_base = "../../covert_dist/app_repo/bundle"
covert_base = "../../covert_dist"

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

		#send JSON to Front End
		print("{\"ack\":\"ok\"}")
		# if true:
		# else :
	except:
		cgi.print_exception()