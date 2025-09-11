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
        """
        서버로부터 메시지를 지속적으로 수신하는 메서드
        - 별도 쓰레드에서 실행되어 사용자 입력과 동시에 처리됨
        - 다른 사용자의 메시지, 입장/퇴장 알림, 귓속말 등을 실시간으로 받음
        """
        while self.connected:
            try:
                data = self.sock.recv(1024)  # 서버로부터 데이터 수신
                
                if not data:  # 서버 연결이 끊어진 경우
                    break
                    
                message = data.decode('utf-8')  # 바이트를 문자열로 변환
                print(message, end='')  # 받은 메시지 화면에 출력
                
            except:
                break  # 네트워크 오류시 루프 종료
                
        self.connected = False

    def send_message(self, message):
        """
        서버에 메시지 전송
        - 사용자가 입력한 텍스트를 서버로 보냄
        - 일반 채팅, 귓속말(/귓), 종료(/종료) 모두 이 메서드 사용
        """
        try:
            self.sock.sendall((message + '\n').encode('utf-8'))
        except:
            self.connected = False  # 전송 실패시 연결 상태 업데이트

    def disconnect(self):
        """
        서버와의 연결 정리 및 소켓 종료
        - 프로그램 종료시 또는 오류 발생시 호출
        """
        self.connected = False
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


if __name__ == '__main__':
    """
    프로그램 실행부
    - ChatClient 인스턴스 생성 후 시작
    - 기본 설정: localhost(127.0.0.1), 포트 5000
    """
    ChatClient().start()