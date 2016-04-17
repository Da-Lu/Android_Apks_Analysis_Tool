#!/usr/bin/python3

# Turn on debug mode.
import os
import cgi
import cgitb
cgitb.enable()

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
def getData():
	formData = cgi.FieldStorage()
	apks = formData["apks[]"]
	return apks

#main program
if __name__ == "__main__" :
	try:
		htmlTop()
		formData = cgi.FieldStorage()
		apks = formData["apks[]"][1]
		# file_data = getData()[0].value
		print(apks)
		# with open ('fileToWrite.apk','w') as fileOutput:
		# 	fileOutput.wirte(file_data)
		# 	fileOutput.close()
		htmlTail()
	except:
		cgi.print_exception()
