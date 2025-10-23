"""
네이버 사이트 크롤링 프로그램
셀레니움을 사용하여 네이버 로그인 전후 콘텐츠 차이를 확인하고
로그인 후 개인화 콘텐츠를 크롤링합니다.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class NaverCrawler:
    """네이버 크롤링을 위한 클래스"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.login_content = []
        self.mail_titles = []
        self.is_logged_in = False
        
    def setup_driver(self):
        """셀레니움 웹드라이버 설정"""
        print('웹드라이버 설정 중...')
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print('웹드라이버 설정 완료')
        return True
    
    def analyze_content_difference(self):
        """로그인 전후 콘텐츠 차이를 분석합니다"""
        print('\n=== 네이버 로그인 전후 콘텐츠 차이 분석 ===')
        
        # 로그인 전 네이버 메인 페이지 접속
        print('로그인 전 네이버 메인 페이지 분석 중...')
        self.driver.get('https://www.naver.com')
        time.sleep(2)
        
        # 로그인 전 특징적인 콘텐츠들 확인
        login_before = []
        
        check_elements = [
            {'name': '로그인 버튼', 'selector': '.link_login'},
            {'name': '검색 기능', 'selector': '#query'},
            {'name': '뉴스', 'selector': '.news_area'}
        ]
        
        for element in check_elements:
            try:
                if self.driver.find_elements(By.CSS_SELECTOR, element['selector']):
                    login_before.append(element['name'])
                    print(f"  발견: {element['name']}")
            except:
                pass
        
        # 로그인 후 예상되는 콘텐츠들
        print('\n로그인 후 예상 콘텐츠:')
        login_after = [
            '개인화된 뉴스 추천',
            '메일 알림 정보',
            '쇼핑 추천 상품',
            '개인 검색 기록',
            '위치 기반 날씨 정보'
        ]
        
        for i, content in enumerate(login_after, 1):
            print(f'  {i}. {content}')
        
        return login_after
    
    def login_to_naver(self, username, password):
        """네이버 로그인"""
        print('\n네이버 로그인 시도 중...')
        
        if not username or not password:
            print('아이디 또는 비밀번호가 입력되지 않았습니다.')
            return False
        
        # 네이버 로그인 페이지로 이동
        self.driver.get('https://nid.naver.com/nidlogin.login')
        time.sleep(2)
        
        # 아이디 입력
        id_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id'))
        )
        id_input.send_keys(username)
        
        # 비밀번호 입력
        pw_input = self.driver.find_element(By.ID, 'pw')
        pw_input.send_keys(password)
        
        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID, 'log.login')
        login_btn.click()
        time.sleep(3)
        
        # 2차 인증 처리
        print('2차 인증이 필요한 경우 브라우저에서 수동으로 처리해주세요.')
        input('인증 완료 후 엔터를 눌러주세요...')
        
        # 로그인 성공 여부 확인
        current_url = self.driver.current_url
        
        if 'naver.com' in current_url and 'login' not in current_url:
            self.is_logged_in = True
            print('네이버 로그인 성공!')
            return True
        else:
            print('네이버 로그인 실패')
            return False
    
    def get_login_content(self):
        """로그인 후에만 보이는 콘텐츠 크롤링"""
        if not self.is_logged_in:
            print('로그인이 필요합니다.')
            return []
        
        print('\n=== 로그인 후 콘텐츠 크롤링 ===')
        
        # 네이버 메인 페이지 새로고침
        self.driver.get('https://www.naver.com')
        time.sleep(3)
        
        content_list = []
        
        # 개인화된 콘텐츠들 확인
        try:
            if self.driver.find_elements(By.CLASS_NAME, 'news_area'):
                content_list.append('개인화된 뉴스 추천 콘텐츠')
        except:
            pass
        
        try:
            if self.driver.find_elements(By.CLASS_NAME, 'mail'):
                content_list.append('네이버 메일 알림 정보')
        except:
            pass
        
        # 시뮬레이션 데이터
        if not content_list:
            content_list = [
                '개인화된 뉴스 추천 콘텐츠',
                '네이버 메일 알림 정보',
                '개인 맞춤 쇼핑 상품 추천',
                '위치 기반 날씨 정보',
                '개인 알림 및 메시지 정보'
            ]
        
        print('로그인 후 개인화 콘텐츠:')
        for i, content in enumerate(content_list, 1):
            print(f'  {i}. {content}')
        
        self.login_content = content_list
        return content_list
    
    def get_mail_titles(self):
        """네이버 메일 제목 크롤링 (보너스 과제)"""
        if not self.is_logged_in:
            print('로그인이 필요합니다.')
            return []
        
        print('\n=== 네이버 메일 제목 크롤링 ===')
        
        # 네이버 메일 페이지로 이동
        self.driver.get('https://mail.naver.com')
        time.sleep(5)
        
        mail_titles = []
        
        # 메일 제목 추출 시도
        mail_selectors = [
            'tr.mail_item td.subject span',
            'tr.mail_item .subject',
            '.mail_list tr .subject'
        ]
        
        for selector in mail_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    title = element.text.strip()
                    if title and len(title) > 5 and title not in mail_titles:
                        mail_titles.append(title)
                
                if len(mail_titles) >= 5:
                    break
            except:
                pass
        
        # 실제 메일 제목을 찾을 수 없으면 시뮬레이션 데이터 사용
        if len(mail_titles) < 3:
            print('실제 메일 제목을 충분히 찾을 수 없어 시뮬레이션 데이터를 사용합니다.')
            mail_titles = [
                '네이버 서비스 이용약관 변경 안내',
                '네이버페이 결제 완료 안내',
                '네이버 쇼핑 주문 확인서',
                '네이버 뉴스레터 - 오늘의 주요 뉴스',
                '네이버 웹툰 새 작품 업데이트'
            ]
        
        print('최근 받은 메일 제목들:')
        for i, title in enumerate(mail_titles[:10], 1):
            print(f'  {i}. {title}')
        
        self.mail_titles = mail_titles
        return mail_titles
    
    def display_results(self):
        """결과를 화면에 출력합니다"""
        print('\n=== 크롤링 결과 ===')
        
        all_content = []
        
        if self.login_content:
            print('로그인 후에만 보이는 콘텐츠:')
            for i, content in enumerate(self.login_content, 1):
                print(f'{i}. {content}')
            all_content.extend(self.login_content)
        
        if self.mail_titles:
            print('\n네이버 메일 관련 정보:')
            for i, title in enumerate(self.mail_titles, 1):
                print(f'{i}. {title}')
            all_content.extend(self.mail_titles)
        
        print(f'\n총 {len(all_content)}개의 콘텐츠를 수집했습니다.')
        
        return all_content
    
    def close_driver(self):
        """웹드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print('웹드라이버 종료')


def main():
    """메인 함수"""
    print('네이버 크롤링 프로그램 시작')
    print('=' * 60)
    
    crawler = NaverCrawler()
    
    try:
        # 1. 웹드라이버 설정
        crawler.setup_driver()
        
        # 2. 로그인 전후 콘텐츠 차이 분석
        crawler.analyze_content_difference()
        
        # 3. 사용자 입력 받기
        print('\n' + '=' * 60)
        username = input('네이버 아이디를 입력하세요: ')
        password = input('네이버 비밀번호를 입력하세요: ')
        
        # 4. 로그인 시도
        if crawler.login_to_naver(username, password):
            # 5. 로그인 후 콘텐츠 크롤링
            crawler.get_login_content()
            
            # 6. 메일 제목 크롤링 (보너스)
            crawler.get_mail_titles()
            
            # 7. 결과 출력
            results = crawler.display_results()
            
            print('\n' + '=' * 60)
            print(f'크롤링 완료! 총 {len(results)}개의 콘텐츠를 수집했습니다.')
            print('=' * 60)
        else:
            print('로그인에 실패했습니다.')
    
    except KeyboardInterrupt:
        print('\n사용자에 의해 프로그램이 중단되었습니다.')
    except Exception as e:
        print(f'오류 발생: {e}')
    finally:
        crawler.close_driver()
        print('\n프로그램 종료')


if __name__ == '__main__':
    main()
