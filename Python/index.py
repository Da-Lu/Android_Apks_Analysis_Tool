#!/usr/bin/python

# Turn on debug mode.
import cgi
import cgitb
cgitb.enable()

# Print necessary headers.
print("""Content-Type: text/html\n\n
	<!DOCTYPE html>
	<html>
		<head>
			<title>Python Server</title>
		</head>
		<body>
			Welcome to Python!
		</body>
	</html>""")
