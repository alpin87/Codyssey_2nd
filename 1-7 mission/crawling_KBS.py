import requests
from bs4 import BeautifulSoup
import re


def get_kbs_headlines():
    url = 'http://news.kbs.co.kr/news/pc/main/main.html'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        print(f'KBS 사이트 응답 상태: {response.status_code}')
        
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        links = soup.find_all('a')
        
        for link in links:
            text = link.get_text().strip()
            
            time_pattern = r'^\d{1,2}:\d{2}'
            
            if (text and 
                len(text) > 10 and 
                len(text) < 150 and 
                not text.startswith('http') and 
                not re.match(time_pattern, text) and
                not text in ['더보기', 'ON AIR', 'English', '재난포털', '제보', '로그인', '회원가입', '메뉴', '검색'] and
                any(keyword in text for keyword in ['…', '·', ':', '(', ')', '"', ''', ''', '대통령', '정부', '국회', '경제', '사회', '정치', '국제', '북한', '중국', '미국', '일본'])):
                headlines.append(text)
        
        unique_headlines = []
        for headline in headlines:
            if headline not in unique_headlines:
                unique_headlines.append(headline)
        
        print(f'추출된 헤드라인 개수: {len(unique_headlines)}')
        
        return unique_headlines[:10] if unique_headlines else ['KBS 헤드라인을 찾을 수 없습니다']
        
    except requests.RequestException as e:
        print(f'KBS 뉴스 데이터를 가져오는 중 오류가 발생했습니다: {e}')
        return ['KBS 사이트 접근 실패']
    except Exception as e:
        print(f'KBS 뉴스 처리 중 오류가 발생했습니다: {e}')
        return ['KBS 뉴스 처리 실패']


def get_weather_info():
    try:
        url = 'https://search.naver.com/search.naver?query=서울날씨'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        weather_info = soup.select_one('.weather_info')
        if weather_info:
            weather_text = weather_info.get_text(strip=True)
            
            temp_match = re.search(r'현재 온도([\d.]+)°', weather_text)
            weather_match = re.search(r'오늘의 날씨(\w+)', weather_text)
            humidity_match = re.search(r'습도(\d+)%', weather_text)
            
            if temp_match and weather_match:
                temp = temp_match.group(1)
                weather = weather_match.group(1)
                humidity = humidity_match.group(1) if humidity_match else None
                
                result = f'서울: {weather}, {temp}°C'
                if humidity:
                    result += f', 습도 {humidity}%'
                return result
            else:
                return '서울: 날씨 정보 파싱 실패'
        else:
            return '서울: 날씨 정보를 찾을 수 없음'
                
    except Exception as e:
        return '서울: 날씨 정보 가져오기 실패'


def main():
    print('=== KBS 뉴스 헤드라인 크롤링 ===')
    
    kbs_headlines = get_kbs_headlines()
    
    print('\n[KBS 헤드라인 목록]')
    for i, headline in enumerate(kbs_headlines, 1):
        print(f'{i}. {headline}')
    
    print('\n=== 보너스: 오늘의 날씨 ===')
    weather = get_weather_info()
    print(weather)


if __name__ == '__main__':
    main()