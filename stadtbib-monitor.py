import requests
# from botocore.vendored import requests
import json
from pprint import pprint
from lxml import html
import re
import datetime
import os


def lambda_handler(event, context):
    url_c = 'https://bibliothek.moenchengladbach.de/opax/de/login.html.S'
    url_l = 'https://bibliothek.moenchengladbach.de/opax/login.S'

    user = os.environ['USER']
    pwd = os.environ['PWD']

    if user == '' or pwd == '':
        return {
            'statusCode': 401,
            'body': json.dumps('USER or PWD missing.')
        }

    def get_full_title_by_id(bookid):
        url = 'https://bibliothek.moenchengladbach.de/opax/ftitle.S'
        params = {'LANG': 'de', 'FUNC': 'full', 'DUM1': '0', bookid: 'YES'}
        r = requests.get(url, params=params)
        tree = html.fromstring(r.content)
        title = tree.xpath('//table/tr/td[@class="td01x09b"]/text() | //table/tr/td[@class="td01x09n"]/text()')
        title = list(map(str.strip, title))

        titles = []
        for i in range(len(title)):
            if title[i] == 'Titel':
                titles.append(title[i + 1])

        return ' '.join(titles)

    r = requests.get(url_c)
    LB = r.cookies['LB']
    cookies = dict(LB=LB)
    data = {'LANG': 'de', 'FUNC': 'login', 'DUM1': '', 'BENUTZER': user, 'PASSWORD': pwd}

    r = requests.post(url_l, cookies=cookies, data=data)

    tree = html.fromstring(r.content)

    dates = tree.xpath('/html/body/div/form/table/tr[@valign]/td[@class="td01b1 td01x09n"]/text()')
    full_ids = tree.xpath('/html/body/div/form/table/tr[@valign]/td/a/attribute::href')

    regex_date = re.compile(r'\d\d\.\d\d\.\d\d\d\d$')
    dates = [i for i in dates if regex_date.match(i)]
    ids = []
    for i in full_ids:
        ids.append(re.sub(r'.*,\'(\d+)\'\).*', r'\g<1>', i))

    now = datetime.datetime.now().date()
    mail_content = []
    subject = ''
    for (date, ID) in zip(dates, ids):
        this = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        date_diff = abs((this - now).days)
        if date_diff < 5:
            title = get_full_title_by_id(ID)
            subject = 'Reminder'
            if date_diff < 2:
                subject = 'Dringend'
            tmp = '{}: Faellig am {} in {} Tagen - title {}'.format(subject, date, date_diff, title)
            mail_content.append(tmp)

    if len(mail_content) != 0:
        text = ''
        for txt in mail_content:
            text += txt + '\n'
        send_mailgun(text, 'Stadtbibliothek {}'.format(subject), user)

    return {
        'statusCode': 200,
        'body': json.dumps(mail_content)
    }


def send_mailgun(text, subject, account_number):
    base_api_url = os.environ['BASEURL']
    api_key = os.environ['APIKEY']
    sender = os.environ['SENDER']
    recipients = os.environ['RECIPIENTS']
    account_name = os.environ['UNAME']
    text = "Konto {} ({})\n\n{}".format(account_name, str(account_number), text)
    data = {'from': sender, 'to': recipients, 'subject': subject, 'text': text}
    r = requests.post(base_api_url + 'messages', data=data, auth=('api', api_key))
    # todo add handling for r.status_code != 200, return proper result

if __name__ == '__main__':
    result = lambda_handler([], [])
