import socket
import threading


class ChatClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False

    def start(self):
        if not self.connect_to_server():
            return
            
        name = input('사용자 이름을 입력하세요: ')
        self.send_message(name)
        
        self.start_receiving_thread()
        self.start_input_loop()

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            return True
        except:
            print('서버에 연결할 수 없습니다.')
            return False

    def start_receiving_thread(self):
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

    def start_input_loop(self):
        try:
            while self.connected:
                message = input()
                self.send_message(message)
                
                if message == '/종료':
                    self.connected = False
                    break
        except KeyboardInterrupt:
            self.send_message('/종료')
        finally:
            self.disconnect()

    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(1024)
                
                if not data:
                    break
                    
                message = data.decode('utf-8')
                print(message, end='')
                
            except:
                break
                
        self.connected = False

    def send_message(self, message):
        try:
            self.sock.sendall((message + '\n').encode('utf-8'))
        except:
            self.connected = False

    def disconnect(self):
        self.connected = False
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


if __name__ == '__main__':
    ChatClient().start()