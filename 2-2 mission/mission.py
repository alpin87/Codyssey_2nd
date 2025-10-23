#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HTML 메일 발송 시스템 - 네이버 기준."""

import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time


def read_csv(filename):
    """CSV에서 수신자 읽기."""
    recipients = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    name = email.split('@')[0]
                    recipients.append((name, email))
    except FileNotFoundError:
        print(f'오류: {filename} 파일이 없습니다.')
        return []
    return recipients


def create_message(sender, name, email, subject, html):
    """HTML 메시지 생성."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = email
    msg.attach(MIMEText(html.replace('{name}', name), 'html', 'utf-8'))
    return msg


def send_individual(sender, password, recipients, subject, html):
    """개별 발송."""
    success = fail = 0
    
    with smtplib.SMTP('smtp.naver.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        for name, email in recipients:
            try:
                smtp.send_message(create_message(sender, name, email, subject, html))
                print(f'✓ {email}')
                success += 1
                time.sleep(1)
            except Exception as e:
                print(f'✗ {email}: {e}')
                fail += 1
    return success, fail


def send_bulk(sender, password, recipients, subject, html):
    """일괄 발송."""
    with smtplib.SMTP('smtp.naver.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        msg = create_message(sender, '회원', sender, subject, html)
        msg['Bcc'] = ', '.join([e for _, e in recipients])
        smtp.send_message(msg)
    print(f'✓ {len(recipients)}명 발송')


def main():
    """메인."""
    print('='*50)
    print('네이버 메일 발송 시스템')
    print('='*50)
    
    # CSV 파일 읽기
    csv_file = 'mail_target_list.csv'
    recipients = read_csv(csv_file)
    
    if not recipients:
        print(f'\n{csv_file} 파일이 없거나 비어있습니다.')
        return
    
    print(f'\n✓ {csv_file} 파일 읽기 완료')
    print(f'수신자: {len(recipients)}명')
    for name, email in recipients:
        print(f'  - {email}')
    
    # 네이버 설정
    print('\n[네이버 메일 설정]')
    print('※ 아이디가 아닌 전체 이메일 주소를 입력하세요')
    sender = input('네이버 이메일 (예: your_id@naver.com): ').strip()
    
    # @naver.com 자동 추가
    if '@' not in sender:
        sender = sender + '@naver.com'
        print(f'→ {sender}')
    
    password = input('비밀번호: ').strip()
    
    # 네이버 IMAP/SMTP 설정 확인
    print('\n※ 네이버 메일 → 환경설정 → POP3/IMAP 설정 → IMAP/SMTP 사용 "사용함"으로 설정')
    confirm = input('설정 완료했나요? (y/n): ').lower()
    if confirm != 'y':
        print('네이버 메일 설정을 먼저 완료해주세요.')
        return
    
    # HTML 템플릿
    html = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body{{font-family:'Malgun Gothic',Arial;margin:0;padding:0}}
.box{{max-width:600px;margin:20px auto;border:1px solid #ddd}}
.head{{background:#03C75A;color:#fff;padding:20px;text-align:center}}
.body{{padding:30px}}
</style></head>
<body><div class="box">
<div class="head"><h1>네이버 메일</h1></div>
<div class="body"><p><strong>{name}</strong>님 안녕하세요!</p>
<p>네이버 SMTP를 통한 HTML 메일 발송 테스트입니다.</p>
<ul><li>개인화된 메시지</li><li>HTML 스타일링</li><li>CSV 기반 발송</li></ul>
</div></div></body></html>'''
    
    # 발송 방식 선택
    print('\n[발송 방식]')
    print('1. 개별 발송 (권장)')
    print('2. 일괄 발송')
    choice = input('선택 (1/2): ').strip()
    
    print('\n[발송 시작]')
    try:
        if choice == '1':
            s, f = send_individual(sender, password, recipients, '네이버 HTML 메일', html)
            print(f'\n결과: 성공 {s}, 실패 {f}')
        else:
            send_bulk(sender, password, recipients, '네이버 HTML 메일', html)
            print('\n발송 완료')
    except Exception as e:
        print(f'\n오류: {e}')
        print('\n해결 방법:')
        print('1. 네이버 메일 로그인 확인')
        print('2. 네이버 메일 → 환경설정 → POP3/IMAP 설정 → 사용함')
        print('3. 2단계 인증 사용 시 앱 비밀번호 필요')


if __name__ == '__main__':
    main()