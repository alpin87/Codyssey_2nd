import argparse
import mimetypes
import os
import smtplib
import socket
import ssl
from email.message import EmailMessage


def build_message(sender, recipient, subject, body, attachment_path=None):
    """Create an EmailMessage with optional single attachment.

    Strings use single quotes by default as per constraints.
    """
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)

    if attachment_path:
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(attachment_path, 'rb') as file:
            file_bytes = file.read()
        filename = os.path.basename(attachment_path)
        message.add_attachment(
            file_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )

    return message


def send_mail(sender, password, recipient, subject, body, attachment_path=None,
              smtp_server='smtp.gmail.com', port=587):
    """Send an email via Gmail SMTP with STARTTLS.

    Exceptions are raised for the caller to handle.
    """
    message = build_message(sender, recipient, subject, body, attachment_path)
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, port, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        server.send_message(message)


def main():
    parser = argparse.ArgumentParser(description='Send email via Gmail SMTP (STARTTLS).')
    parser.add_argument('--sender', required=False, default=os.getenv('GMAIL_SENDER'), help='Gmail 주소')
    parser.add_argument('--to', required=False, default=os.getenv('MAIL_TO'), help='수신자 이메일 주소')
    parser.add_argument('--subject', required=False, default=os.getenv('MAIL_SUBJECT', '테스트 메일'), help='메일 제목')
    parser.add_argument('--body', required=False, default=os.getenv('MAIL_BODY', '본문입니다.'), help='메일 본문')
    parser.add_argument('--password', required=False, default=os.getenv('GMAIL_APP_PASSWORD'), help='Gmail 앱 비밀번호')
    parser.add_argument('--attach', required=False, default=None, help='첨부 파일 경로(선택)')

    args = parser.parse_args()

    if not args.sender or not args.to or not args.password:
        print('필수 정보 누락: --sender, --to, --password 또는 환경변수를 설정하세요.')
        print('예) setx GMAIL_SENDER your@gmail.com, setx GMAIL_APP_PASSWORD abcd...., setx MAIL_TO target@domain')
        raise SystemExit(2)

    try:
        send_mail(
            sender=args.sender,
            password=args.password,
            recipient=args.to,
            subject=args.subject,
            body=args.body,
            attachment_path=args.attach,
        )
    except FileNotFoundError as error:
        print(f'첨부 파일을 찾을 수 없습니다: {error}')
        raise SystemExit(1)
    except smtplib.SMTPAuthenticationError as error:
        print(f'인증 실패: {error}')
        raise SystemExit(1)
    except smtplib.SMTPConnectError as error:
        print(f'SMTP 연결 실패: {error}')
        raise SystemExit(1)
    except (socket.gaierror, TimeoutError, socket.timeout) as error:
        print(f'네트워크 오류: {error}')
        raise SystemExit(1)
    except smtplib.SMTPException as error:
        print(f'SMTP 오류: {error}')
        raise SystemExit(1)
    except Exception as error:  # 최후의 방어선
        print(f'알 수 없는 오류: {error}')
        raise SystemExit(1)
    else:
        print('메일이 성공적으로 발송되었습니다.')


if __name__ == '__main__':
    main()


