import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import datetime
from datetime import datetime, timedelta
import re



def sending_mail(from_email_id: str,
                 from_email_pw: str, 
                 to_email: list,
                 contents: str) -> None:
    
    today = datetime.now().strftime("%y년 %m월 %d일")
    scarp_day = (datetime.now()-timedelta(days=1)).strftime("%m월 %d일")


    msg_title = f"[{today}] {scarp_day} 뉴스 스크랩"
 
 
    recipients = []
    for to_ in to_email:
        recipients.append(to_)


    msg = MIMEMultipart()
    msg['Subject'] = msg_title
    msg['From'] = from_email_id
    msg['To'] = ",".join(recipients)

    content = \
    f"""
    <html>
        <body>
    {contents}
        </body>
    </html>
    """

    mimetext = MIMEText(content, 'html')
    msg.attach(mimetext)


    if re.search("@gmail.com", from_email_id):
        server = smtplib.SMTP('smtp.gmail.com', 587) #587 #465
    else:
        server = smtplib.SMTP('smtp.naver.com', 587) #587 #465 


    server.ehlo()
    server.starttls()
    server.login(from_email_id, from_email_pw)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] 파일전송 완료")




def sending_error_mail(from_email_info: dict, 
                       to_email: list,
                       contents: str) -> None:
    
    today = datetime.now().strftime("%y년 %m월 %d일")
    
    

    
    # togo_file_name = today +"_TLE(re).txt"
    msg_title = today + f"{contents} crawler error 발생"
 
 
    recipients = []
    for to_ in to_email:
        recipients.append(to_)


    msg = MIMEMultipart()
    msg['Subject'] = msg_title
    msg['From'] = from_email_info['email']
    msg['To'] = ",".join(recipients)

    content = \
    f"""
    """

    mimetext = MIMEText(content, 'html')
    msg.attach(mimetext)


    if re.search("@gmail.com", from_email_info['email']):
        server = smtplib.SMTP('smtp.gmail.com', 587) #587 #465
    else:
        server = smtplib.SMTP('smtp.naver.com', 587) #587 #465 


    server.ehlo()
    server.starttls()
    server.login(from_email_info['email'],from_email_info['pw'])
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {contents} crawler error 발생")