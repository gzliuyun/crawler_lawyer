#__author__ = 'Administrator'
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import MySQLdb

con= MySQLdb.connect(host='localhost',user='root',passwd='123456',db='predict',charset='utf8')
cursor =con.cursor()
dealed = []
cphone  = []
def readPage(url_page):
    global cphone
    cphone = []

    url_part1 = url_page[0:url_page.rfind('/')]
    url_part2 = url_page[url_page.rfind('/')+1:url_page.rfind('ll')]
    url_part3 = url_page[url_page.rfind('ll'):len(url_page)]

    start = int(url_part2[1:len(url_part2)])
    index = start
    while index :
        url_all = url_part1 + "/p"+str(index)+url_part3
        print url_all

        if not getURL(url_all):
            break
        index += 1


def getURL(pageurl):

    request = urllib2.Request(pageurl)
    response = urllib2.urlopen(request)
    html = response.read()

    soup = BeautifulSoup(html)
    list =  soup.find_all("div",class_ = 'name_ph')
    if len(list) == 0:
        return False
    lawyers_url = []
    cp = ''
    global cphone
    for url in list:
        if str(url.span.__class__) != "<type 'NoneType'>":
            cp = url.span.string.strip()
            if cp in cphone:
                continue
            else:
                cphone.append(cp)
        lawyers_url.append(url.a['href'])

    for url in lawyers_url:
        try:
            find_lawyer(url)
        except:
            continue
    return True

def find_lawyer(url):
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        html = response.read()
    except:
        return
    soup = BeautifulSoup(html)
    haveName = soup.find('div',class_ ='lawyer-msg fr')

    if str(haveName.__class__) == "<type 'NoneType'>":
        haveName = soup.find('div',class_ ='imgText_110_135').find('h4')
        name = haveName.text.strip().encode('utf-8')

    else :
        haveName = haveName.find('a')
        name = haveName.string.encode('utf-8')
    name = name[0:name.find('律师')]
    print name,

    intro_url = url.replace('lll','int')
    try:
        introduction , type = get_introduction(intro_url)
    except:
        return

    print type,
    # 提取个人信息
    if type == 'yellow':
        childs = soup.find('div',class_ = 'lawyer-info').find_all('p')
        for index in range(len(childs)):
            text = childs[index].text.encode('utf-8')
            if index == 1:
                area = text[text.find('：')+len('：'):len(text)]
            if index == 2:
                cellphone = text[text.find('：')+len('：'):len(text)]
            if index == 3:
                office_phone = text[text.find('：')+len('：'):len(text)]
            if index == 4:
                email = text[text.find('：')+len('：'):len(text)]
            if index == 6:
                carrer_id = text[text.find('：')+len('：'):text.find(' ')]
            if index == 7:
                organization = text[text.find('：')+len('：'):len(text)]
    elif type == 'blue':
        childs = soup.find('div',class_ = 'lawyer-info').find_all('p')
        for index in range(len(childs)):
            text = childs[index].text.encode('utf-8')
            if index == 0:
                area = text[text.find('：')+len('：'):len(text)]
            if index == 3:
                cellphone = text[text.find('：')+len('：'):len(text)]
            if index == 4:
                office_phone = text[text.find('：')+len('：'):len(text)]
            if index == 6:
                carrer_id = text[text.find('：')+len('：'):len(text)]
            if index == 7:
                organization = text[text.find('：')+len('：'):len(text)]
        email = ''
    elif type == 'other':
        childs = soup.find('div',class_ = 'moduleContent').find_all('li')
        for index in range(len(childs)):
            text = childs[index].text.encode('utf-8').strip()
            if index == 0:
                cellphone = text[text.find('：')+len('：'):text.rfind(' ')].strip()
            if index == 2:
                email =  text[text.find('：')+len('：'):len(text)].strip()
            if index == 3:
                carrer_id = text[text.find('：')+len('：'):len(text)].strip()
            if index == 4:
                organization = text[text.find('：')+len('：'):len(text)].strip()
        office_phone = ''
        area = ''

    # 提取擅长领域
    skills = ''
    if type == 'yellow':
        skill_list = soup.find('div',class_ = 'btn-main hauto')
        if str(skill_list.__class__) == "<class 'bs4.element.Tag'>":
            skill_list = skill_list.find_all('a')
            for k in skill_list:
                skills += k.text+" "
            skills = skills[0:-1].encode('utf-8')
    elif type == 'other':
        skill_list = soup.find('div',class_ = 'lingyu')
        if str(skill_list.__class__) == "<class 'bs4.element.Tag'>":
            skill_list = skill_list.find_all('li')
            for k in skill_list:
                skills += k.text+" "
            skills = skills[0:-1].encode('utf-8')
    # type == 'blue'时，没有擅长领域
    print '--',
    faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei = fingWords(introduction)

    infor_source = intro_url.encode('utf-8')

    sql = '''insert into lawyers(name,area,career_id,organization,office_phone,cellphone,email,skill,
            introduction,faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei,infor_source) values
            ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(name,
            area,carrer_id,organization,office_phone,cellphone,email,skills,introduction,faguan,fayuan,
            jianchaguan,jianchayuan,gongan,zhengfawei,infor_source)
    print '**'

    insertData(sql)

def get_introduction(url):
    introduction = ''
    type = ''

    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    html = response.read()


    soup = BeautifulSoup(html)
    childs = soup.find('div',class_ = 'article-cont')
    type = 'yellow'

    if str(childs.__class__) == "<type 'NoneType'>":
        childs = soup.find('div',class_ = 'cont-a hauto')
        type = 'blue'

    if str(childs.__class__) == "<type 'NoneType'>":
        childs = soup.find('div',class_ = 'archives').find_all('div',class_ = 'text',limit = 1)
        type = 'other'

    for child in childs:
        if str(child.__class__) == "<class 'bs4.element.Tag'>":
            introduction += child.text.strip()
        else:
            introduction += child.strip()
    if type != 'yellow':
        introduction = introduction[4:len(introduction)]
    introduction = introduction.strip()

    return introduction.encode('utf-8'),type

def fingWords(introduction):
    if introduction.find('法官') == -1:
        faguan = '0'
    else:
        faguan = '1'
    if introduction.find('法院') == -1:
        fayuan = '0'
    else:
        fayuan = '1'
    if introduction.find('检查官') == -1:
        jianchaguan = '0'
    else:
        jianchaguan = '1'
    if introduction.find('检查院') == -1:
        jianchayuan = '0'
    else:
        jianchayuan = '1'
    if introduction.find('公安') == -1:
        gongan = '0'
    else:
        gongan = '1'
    if introduction.find('政法委') == -1:
        zhengfawei = '0'
    else:
        zhengfawei = '1'
    return faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei

def insertData(sql):
    # print sql
    try:
        cursor.execute(sql)
        con.commit()
    except:
        return

def readPlaces():
    f_dealed = open('dealed.txt','r')
    global  dealed
    for f_d in f_dealed.readlines():
        # 添加的时候去掉最后一个换行符
        dealed.append(f_d[0:-1])
    f_dealed.close()

    f = open('places.txt','r')
    for place in f.readlines():
        place = place[0:-1]
        url_place = 'http://www.lawtime.cn/'
        url_place += place + '/lawyer'
        try:
            specialty_lawyers(url_place)
        except:
            continue


# 专业律师
def specialty_lawyers(url):
    count_number=5
    print url
    while count_number:
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            html = response.read()
            count_number=0
        except:
            count_number-=1
    soup = BeautifulSoup(html)
    type_list = soup.find_all('dd',limit=5)
    index = 0
    for tp in type_list:
        index += 1
        now = 0
        for xifen in tp:
            if str(xifen.__class__) == "<class 'bs4.element.Tag'>":
                now += 1
                if index == 1:
                        continue
                elif index == 2:
                    if now != 1 and now !=2:
                        continue
                elif index == 3:
                    if now != 5:
                        continue
                elif index == 4:
                    if now != 1:
                        continue
                elif index == 5:
                    if now != 5 and now!=8:
                        continue
                try:
                    print index,now
                    more_page(str(xifen['href']))
                except:
                    continue
def more_page(url):
    count_number=5
    while count_number:
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            html = response.read()
            count_number=0
        except:
            count_number-=1
    soup = BeautifulSoup(html)
    list = soup.find('div',class_ ='dl_title')
    if list is not None:
        for k in list:
            if str(k.name) == "a":
                url = str(k['href'])

    global dealed
    f_dealed = open('dealed.txt','a')
    if not url in dealed:
        f_dealed.write(url)
        f_dealed.write('\n')
    else:
        return
    f_dealed.close()

    try:
        readPage(url)
    except:
        return

if __name__ == '__main__':
    readPlaces()
