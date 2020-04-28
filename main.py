import smtplib
from email.mime.text import MIMEText
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def send_notice(notice_list):
    sender = "보내는 사람"
    toList = [ "보낼 사람" ]
    today_text = datetime.today().strftime("%Y-%m-%d %H:%M")
    smtp = smtplib.SMTP('smtp.gmail.com', 587) # SMTP 서버
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, '비밀번호')
    html = """
    <html>
        <head>
	    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        </head>
        <body align="center" style="margin: 0; padding: 0;">
	    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; font-family: sans-serif;">
		<tr style="border-bottom: 0.1rem solid #cccccc">
		    <td style="padding: 0.5rem">
			<a href="http://jbnu.ac.kr/kor"><img src="http://jbnu.ac.kr/kor/images/logo_tr.png" width="150" height="42" style="display: block;"></a>
		    </td>
		</tr>
		<tr style="border-bottom: 0.1rem solid #cccccc">
		    <td style="padding: 1.0rem">
			<div style="color: gray; padding: 0 0 1.0rem 0; font-size: 0.95rem">
			    안녕하세요, 최근 등록된 공지사항을 알립니다.
			    <br />
			    재확인 시간: {0}
			</div>
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
    """.format(today_text)
    for notice in notice_list:
        html += """
			    <tr style="border: 0.1rem solid #cccccc">
				<td width="15%" style="text-align: center; padding: 0.5rem; font-size: 1.0rem;">
				    {0}
				</td>
				<td width="65%" style="word-break:break-all; padding: 0.5rem; font-size: 1.0rem;" wrap="hard">
				    <a style="color: black" href="http://jbnu.ac.kr/kor/?menuID=139&mode=view&no={1}">{2}</a>
				</td>
				<td width="20%" style="text-align: center;">
				    <span style="font-size: 0.85rem">{3}</span>
				</td>
			    </tr>
	""".format(notice[0], notice[1], notice[2], notice[3])
    html += """
			</table>
		    </td>
		</tr>
                <tr>
		    <td style="padding: 0.5rem">
			<p style="float: right; margin: 0; font-size: 0.8rem">Copyright ⓒ 1998-2019 Jeonbuk National University. All rights reserved.</p>
		    </td>
		</tr>
	    </table>
        </body>
    </html>
    """
    msg = MIMEText(html, 'html')
    msg['Subject'] = "[전북대학교 공지사항 알림] " + str(len(notice_list)) + "개의 공지사항이 있습니다."
    msg['From'] = sender
    msg['To'] = ",".join(toList)
    smtp.sendmail(sender, toList, msg.as_string())
    smtp.close()
    

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

before_notice = 0
with open(os.path.join(BASE_DIR, 'latest.txt'), 'r+') as f_read:
    before_notice = int(f_read.readline())
    f_read.close()

notice_list = []
latest_notice = 0

for i in range(10):
    req = requests.get('http://jbnu.ac.kr/kor/?menuID=139&pno=' + str(i + 1))
    req.encoding = 'utf-8'
    
    soup = BeautifulSoup(req.text, 'html.parser')
    table = soup.find('table', {'class': 'ta_bo'})
    tbody = table.find("tbody")
    tr_list = tbody.find_all("tr")
    for tr in tr_list:
        notice_number = int(tr.find('td', {'class': 'left'}).find('a')['href'].split('=')[-1])
        if latest_notice < notice_number:
            latest_notice = notice_number
        if notice_number <= before_notice:
            if tr.find('th').find('img') is None:
                break;
            else:
                continue;
        td_list = tr.find_all('td')
        notice_group = td_list[0].find('span').get_text().strip()
        notice_subject = td_list[1].find('a').get_text().strip()
        notice_date = tr.find_all('td', {'class': 'mview'})[1].get_text().strip()
        notice_list.append([notice_group, notice_number, notice_subject, notice_date])

if notice_list:
    print("메일 보내는 중 ...")
    send_notice(notice_list)
    print("메일 보내기 완료!")
    
with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
    f_write.write(str(latest_notice))
    f_write.close()
    print("최근 공지 정보 수정 완료!")
