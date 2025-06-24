import sys
import os
import uuid
from glob import glob
from datetime import datetime
import urllib.parse

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html',
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        for kk in headers:
            resp.append(f"{kk}:{headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)

        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        try:
            headers, body = data.split("\r\n\r\n", 1)
            requests = headers.split("\r\n")
            baris = requests[0]
            all_headers = requests[1:]
            j = baris.split(" ")
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers, body)
            else:
                return self.response(400, 'Bad Request', '', {})
        except Exception as e:
            return self.response(400, 'Bad Request', str(e), {})

    def http_get(self, object_address, headers):
        files = os.listdir('./')
        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {'Content-type': 'text/plain'})

        elif object_address == '/list':
            file_list = '\n'.join(files)
            return self.response(200, 'OK', file_list, {'Content-type': 'text/plain'})

        elif object_address.startswith('/delete'):
            _, _, query = object_address.partition('?')
            params = urllib.parse.parse_qs(query)
            filename = params.get('filename', [None])[0]
            if filename:
                filename = os.path.basename(filename)  # ⬅️ tambahkan ini
                if os.path.exists(filename):
                    os.remove(filename)
                    return self.response(200, 'OK', f"{filename} deleted", {'Content-type': 'text/plain'})
            return self.response(404, 'Not Found', 'File not found or invalid', {'Content-type': 'text/plain'})


        elif object_address == '/video':
            return self.response(302, 'Found', '', {'location': 'https://youtu.be/katoxpnTf04'})

        elif object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {'Content-type': 'text/plain'})

        object_address = object_address[1:]  # remove leading '/'
        if not os.path.exists(object_address):
            return self.response(404, 'Not Found', '', {})
        with open(object_address, 'rb') as fp:
            isi = fp.read()
        fext = os.path.splitext(object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')
        return self.response(200, 'OK', isi, {'Content-type': content_type})

    def http_post(self, object_address, headers, body):
        # Ambil nama file dari query string: /upload?filename=testing.txt
        parsed = urllib.parse.urlparse(object_address)
        query = urllib.parse.parse_qs(parsed.query)
        filename = query.get('filename', [None])[0]
    
        if not filename:
            filename = f"upload_{uuid.uuid4().hex}.txt"
        else:
            filename = os.path.basename(filename)  # Mencegah path traversal
    
        with open(filename, 'w') as f:
            f.write(body)
    
        return self.response(200, 'OK', f"File uploaded as {filename}", {'Content-type': 'text/plain'})


