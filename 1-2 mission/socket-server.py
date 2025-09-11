import socket
import threading


class ChatServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(10)
        
        print(f'서버가 {self.host}:{self.port}에서 시작되었습니다.')
        
        try:
            while True:
                conn, addr = server_sock.accept()
                thread = threading.Thread(
                    target=self.handle_client, 
                    args=(conn,), 
                    daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            print('\n서버를 종료합니다.')
        finally:
            server_sock.close()

    def handle_client(self, conn):
        try:
            name = self.receive_message(conn)
            
            if not name:
                conn.close()
                return
                
            self.add_client(conn, name)
            self.broadcast_message(f'{name}님이 입장하셨습니다.')
            
            while True:
                message = self.receive_message(conn)
                
                if not message:
                    break
                    
                if message == '/종료':
                    break
                    
                if message.startswith('/w '):
                    self.process_whisper(conn, name, message)
                    continue
                    
                self.broadcast_message(f'{name}> {message}')
                
        except:
            pass
        finally:
            self.remove_client(conn)

    def process_whisper(self, sender_conn, sender_name, message):
        parts = message.split(' ', 2)
        
        if len(parts) < 3:
            self.send_message(sender_conn, '[서버] 사용법: /w 대상유저 메시지')
            return
            
        target_name = parts[1]
        whisper_msg = parts[2]
        
        target_conn = self.find_client_by_name(target_name)
        
        if target_conn:
            whisper_text = f'[귓속말] {sender_name} → {target_name}: {whisper_msg}'
            self.send_message(target_conn, whisper_text)
            self.send_message(sender_conn, whisper_text)
        else:
            self.send_message(sender_conn, f'[서버] {target_name}을 찾을 수 없습니다.')

    def add_client(self, conn, name):
        with self.lock:
            self.clients[conn] = name

    def remove_client(self, conn):
        with self.lock:
            name = self.clients.pop(conn, None)
            
        try:
            conn.close()
        except:
            pass
            
        if name:
            self.broadcast_message(f'{name}님이 퇴장하셨습니다.')

    def find_client_by_name(self, name):
        with self.lock:
            for conn, client_name in self.clients.items():
                if client_name == name:
                    return conn
        return None

    def broadcast_message(self, message):
        disconnected = []
        
        with self.lock:
            for conn in self.clients.keys():
                if not self.send_message(conn, message):
                    disconnected.append(conn)
        
        self.cleanup_disconnected_clients(disconnected)

    def cleanup_disconnected_clients(self, disconnected):
        for conn in disconnected:
            self.remove_client(conn)

    def send_message(self, conn, message):
        try:
            conn.sendall((message + '\n').encode('utf-8'))
            return True
        except:
            return False

    def receive_message(self, conn):
        try:
            data = conn.recv(1024)
            
            if not data:
                return None
                
            return data.decode('utf-8').strip()
        except:
            return None


if __name__ == '__main__':
    ChatServer().start()