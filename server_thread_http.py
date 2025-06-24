from socket import *
import socket
import threading
import logging
import sys
from http import HttpServer  # Pastikan http_server.py memiliki kelas HttpServer

httpserver = HttpServer()

# Konfigurasi logging agar tampil ke terminal
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')


class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        self.connection.settimeout(3)
        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    d = data.decode()
                    rcv += d

                    # Periksa apakah sudah akhir dari header
                    if '\r\n\r\n' in rcv:
                        headers, body = rcv.split('\r\n\r\n', 1)

                        # Deteksi Content-Length jika ada body
                        content_length = 0
                        for h in headers.split('\r\n'):
                            if h.lower().startswith('content-length'):
                                try:
                                    content_length = int(h.split(":")[1].strip())
                                except:
                                    content_length = 0
                                break

                        # Jika body belum lengkap, lanjutkan membaca
                        if len(body) < content_length:
                            continue

                        # Proses permintaan
                        logging.warning("data dari client: %s", rcv)
                        hasil = httpserver.proses(rcv)
                        hasil = hasil + "\r\n\r\n".encode()
                        logging.warning("balas ke client: %s", hasil)
                        self.connection.sendall(hasil)
                        break
                else:
                    break
            except socket.timeout:
                logging.warning("Timeout dari client: %s", self.address)
                break
            except Exception as e:
                logging.warning("Exception saat menerima data: %s", str(e))
                break
        self.connection.close()


class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 8889))
        self.my_socket.listen(50)  # Terima sampai 50 koneksi dalam antrian
        logging.warning("Server berjalan di port 8889")
        while True:
            try:
                self.connection, self.client_address = self.my_socket.accept()
                logging.warning("Koneksi dari %s", self.client_address)
                clt = ProcessTheClient(self.connection, self.client_address)
                clt.start()
                self.the_clients.append(clt)
            except KeyboardInterrupt:
                logging.warning("Server dihentikan dengan KeyboardInterrupt")
                break
            except Exception as e:
                logging.warning("Terjadi kesalahan saat menerima koneksi: %s", str(e))


def main():
    svr = Server()
    svr.start()


if __name__ == "__main__":
    main()
