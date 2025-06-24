from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from http import HttpServer

httpserver = HttpServer()

class ProcessTheClient(multiprocessing.Process):
    def __init__(self, conn_fd, address):
        super().__init__()
        self.conn_fd = conn_fd
        self.address = address

    def run(self):
        self.connection = socket.socket(fileno=self.conn_fd)
        try:
            buffer = ""
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break
                buffer += data.decode()

                if '\r\n\r\n' in buffer:
                    header, rest = buffer.split('\r\n\r\n', 1)

                    content_length = 0
                    for line in header.split('\r\n'):
                        if line.lower().startswith("content-length:"):
                            try:
                                content_length = int(line.split(":")[1].strip())
                            except:
                                content_length = 0

                    while len(rest) < content_length:
                        more_data = self.connection.recv(1024)
                        if not more_data:
                            break
                        rest += more_data.decode()

                    full_request = header + '\r\n\r\n' + rest
                    hasil = httpserver.proses(full_request)
                    hasil = hasil + "\r\n\r\n".encode()
                    self.connection.sendall(hasil)
                    break
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            self.connection.close()


class Server(multiprocessing.Process):
    def __init__(self, host='0.0.0.0', port=8889):
        super().__init__()
        self.host = host
        self.port = port
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.my_socket.bind((self.host, self.port))
        self.my_socket.listen(5)
        logging.warning(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                conn, addr = self.my_socket.accept()
                logging.warning(f"Connection from {addr}")
                
                # Ambil file descriptor dan pass ke child process
                conn_fd = conn.fileno()
                client_process = ProcessTheClient(conn_fd, addr)
                client_process.start()
                self.the_clients.append(client_process)

                conn.close()  # Penting: tutup socket di parent agar tidak double-open
        except KeyboardInterrupt:
            logging.warning("Server stopped manually")
        finally:
            self.my_socket.close()
            for p in self.the_clients:
                p.join()


def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server()
    svr.start()
    svr.join()

if __name__ == "__main__":
    main()
