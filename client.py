import socket
import os

HOST = 'localhost'
PORT = 8889
FILENAME = 'testing.txt'
DEFAULT_CONTENT = "Ini File Testing"

def send_request(req):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(req.encode())
        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data
    return response.decode(errors='ignore')

# 1. Cek dan buat file jika belum ada
if not os.path.exists(FILENAME):
    with open(FILENAME, 'w') as f:
        f.write(DEFAULT_CONTENT)
    print(f"File '{FILENAME}' tidak ditemukan, telah dibuat dengan isi default.")

# 2. Baca isi file
with open(FILENAME, 'r') as f:
    file_content = f.read()

# 3. Upload
print("\n=== Upload testing.txt ===")
content_length = len(file_content.encode())  # penting untuk ukuran body
upload_request = (
    f"POST /upload?filename={FILENAME} HTTP/1.0\r\n"
    f"Content-Length: {content_length}\r\n"
    f"\r\n"
    f"{file_content}"
)
upload_response = send_request(upload_request)
print(upload_response)

# 4. List file setelah upload
print("\n=== List Files Setelah Upload ===")
print(send_request("GET /list HTTP/1.0\r\n\r\n"))

# 5. Delete
print("\n=== Delete testing.txt ===")
delete_request = f"GET /delete?filename={FILENAME} HTTP/1.0\r\n\r\n"
delete_response = send_request(delete_request)
print(delete_response)

# 6. List file setelah delete
print("\n=== List Files Setelah Delete ===")
print(send_request("GET /list HTTP/1.0\r\n\r\n"))
