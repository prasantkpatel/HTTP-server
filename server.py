from socket import *
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import os
import stat
import magic
import _thread

crlf = '\r\n'

serverPort=80
sSocket = socket(AF_INET, SOCK_STREAM)

while True:
	try:
		sSocket.bind(('localhost', int(serverPort)))
		break
	except (OSError, PermissionError, ValueError):
		print("Error: Invalid Port/Port already in use, Port: ", serverPort)
		serverPort = input("Please choose other port: ")


sSocket.listen(1)

print('Server listening on port ', serverPort)

def get_file_path(req):
	start = req.find(' ')+1
	url = req[start:start+req[start: ].find(' ')]
	url = url if url.find('http://')==-1 else url[url.find('http://')+7:]
	path = url[url.find('/'):]
	return path.replace('%20', ' ')

def handle_request(connectionSocket, clientAddr):
	keep_alive = True

	while keep_alive:
		try:
			req = connectionSocket.recv(10000).decode('utf-8')

			if req=='':
				continue
			else:
				print(req)

			temp = get_file_path(req)

			if temp.strip()=='/':
				temp='/index.html'
				
			file_path = os.environ['HOME'] + temp
			
			keep_alive = False if req.find('Connection: ')==-1 else (True if req[req.find('Connection: ')+12:req[req.find('Connection: ')+12:].find('\r\n')]=='keep-alive' else False)
			httpres = ''

			try:
				fo = open(file_path, 'rb')
				file_stats = os.stat(file_path)
				httpres = "HTTP/1.1 200 OK"+crlf+"Date: "+format_date_time(mktime(datetime.now().timetuple()))+crlf+"Server: myserver"+crlf+"Last-Modified: "+format_date_time(file_stats[stat.ST_MTIME])+crlf+"Content-Length: "+str(file_stats[stat.ST_SIZE])+crlf+"Content-Type: "+magic.Magic(mime=True).from_file(file_path)+crlf+crlf
				httpres = httpres.encode('utf-8')
				httpres += fo.read()
				fo.close()

			except OSError:
				httpres = "HTTP/1.1 404 Not Found"+crlf+"Date: "+format_date_time(mktime(datetime.now().timetuple()))+crlf+"Server: myserver"+crlf+crlf+""
				httpres = httpres.encode('utf-8')

			finally:
				print("Response Generated: ", httpres)
				connectionSocket.send(httpres)

		except ConnectionResetError:
			print("Connection closed by foreign host", clientAddr)
			return

	connectionSocket.close()
	
while True:
	connectionSocket, clientAddr = sSocket.accept()
	_thread.start_new_thread(handle_request, (connectionSocket, clientAddr))
