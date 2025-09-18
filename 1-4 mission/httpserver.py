import http.server
import socketserver
import datetime


class SimpleHandler(http.server.BaseHTTPRequestHandler):
    """단순한 HTTP 요청 핸들러"""
    
    def do_GET(self):
        """GET 요청 처리"""
        # 접속 정보 출력
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        print(f'접속 시간: {current_time}')
        print(f'접속한 클라이언트 IP: {client_ip}')
        print('-' * 40)
        
        try:
            # index.html 파일 읽기
            with open('index.html', 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 200 응답 전송
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            # index.html이 없을 때
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = '<h1>404 - index.html 파일을 찾을 수 없습니다</h1>'
            self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """기본 로그 메시지 무시"""
        pass


def main():
    """메인 함수"""
    port = 8080
    
    print(f'우주 해적 웹서버 시작 - 포트 {port}')
    print(f'브라우저에서 http://localhost:{port} 접속')
    print('종료: Ctrl+C')
    print('=' * 40)
    
    with socketserver.TCPServer(('', port), SimpleHandler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()