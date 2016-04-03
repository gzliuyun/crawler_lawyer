#__author__ = 'Administrator'
# -*- coding: utf-8 -*-
import urllib
import urllib2
from bs4 import BeautifulSoup
import bs4
import MySQLdb

con= MySQLdb.connect(host='localhost',user='root',passwd='123456',db='predict',charset='utf8')
cursor =con.cursor()
dealed = []

def addPage():
    url1 = 'http://lawyer.9ask.cn/library/lists-'
    url2 = '-0-0-0-0-0-'
    for index in range(2,36):
        url = url1 + str(index) + url2
        getPage(url)

def getPage(url):
    page = 1
    while page:
        url_page = url + str(page) + '.html'
        global dealed
        if not url_page in dealed:
            f_dealed = open('dealed.txt','a')
            f_dealed.write(url_page)
            f_dealed.write('\n')
            f_dealed.close()
        else:
            print url_page
            page += 1
            continue

        if not getLawyer(url_page):
            break
        page += 1

def getLawyer(url):
    print url
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request,timeout=5)
        html = response.read()
    except:
        return False
    soup = BeautifulSoup(html)

    tag = soup.find_all('div',class_ = 'brandItemBox clearfix')
        # for div in tag:
    if len(tag) == 0:
        return False
    for div in tag:
        a = div.find('a')
        link = a['href']
        try:
            infor(link)
        except:
            continue

    return True

def infor(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request,timeout=5)
    html = response.read()
    soup = BeautifulSoup(html)

    name_tag = soup.find('div',class_ = 'webLogoLName')
    if type(name_tag) == bs4.element.Tag:
        name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction = style1(soup)

    else:
        name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction = style2(soup)

    faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei = fingWords(introduction)
    infor_source = url.encode('utf-8')

    sql = '''insert into new_law1_copy(name,area,career_id,organization,office_phone,cellphone,email,skill,
            introduction,faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei,infor_source) values
            ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(name,
            area,carrer_id,organization,office_phone,cellphone,email,skills,introduction,faguan,fayuan,
            jianchaguan,jianchayuan,gongan,zhengfawei,infor_source)

    # print sql
    insertData(sql)

def insertData(sql):
    # print sql
    try:
        cursor.execute(sql)
        con.commit()
    except:
        return

def style1(soup):
    name = ''; area = ''; carrer_id = '';
    organization = ''; office_phone = '';
    cellphone = ''; email = '';
    introduction = '';skills = '';

    name_tag = soup.find('div',class_ = 'webLogoLName')
    name = name_tag.string.encode('utf-8')
    print name
    other = soup.find('div',class_ = 'partOneTopLConTopR')
    index = 1
    for text in other.stripped_strings:
        if index == 1:
            area  = str(text.encode('utf-8')).split('：')[1]
        if index == 3:
            organization = text.encode('utf-8')
        if index == 4:
            carrer_id = str(text.encode('utf-8')).split('：')[1]
        if index == 5:
            office_phone = str(text.encode('utf-8')).split('：')[1]
        if index == 8:
            email = str(text.encode('utf-8')).split('：')[1]
        index += 1
    skills_str = soup.find('div',class_ = 'goodAtField').string.encode('utf-8')

    skills_str = skills_str.replace('        ','')
    skills_str = skills_str.strip().replace('    ','、')
    skills = skills_str.replace('\n','')

    intro_url = soup.find('div',class_ = 'partOneTopLCon').find('p').find('a')['href']
    introduction  = intro(intro_url)

    return name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction

def style2(soup):
    name = ''; area = ''; carrer_id = '';
    organization = ''; office_phone = '';
    cellphone = ''; email = '';
    introduction = '';skills = '';

    name = soup.find('div',class_='left').find('h1').string.encode('utf-8')
    index = name.find('律师')

    name = name[0:name.find('律师')]
    print name
    infor_list = soup.find_all('div',class_='infoSmallBox')
    index = 1
    for tag in infor_list:
        if index == 1:
            try:
                area = tag.contents[4].string.encode('utf-8')
                area = area[1:len(area)-1]
            except:
                pass
        elif index == 3:
            try:
                office_phone = tag.contents[2].string.encode('utf-8')
            except:
                pass
        elif index == 4:
            try:
                email = tag.contents[2].string.encode('utf-8')
            except:
                pass
        elif index == 7:
            try:
                organization = tag.contents[2].string.encode('utf-8')
            except:
                pass
            try:
                carrer_id = tag.contents[4].string.encode('utf-8')
            except:
                pass
        index += 1

    services = soup.find('div',class_='serviceBox clearfix')
    skills = ''
    index = 1
    for ser in services.stripped_strings:

        if index == 1:
            skills += ser.encode('utf-8')
        else:
            skills += str('、')+ser.encode('utf-8')
        index += 1

    infor_tag = soup.find('div',class_='abstractInfo')
    for t in infor_tag.stripped_strings:
        introduction += t
    introduction = introduction.encode('utf-8')
    return name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction

def intro(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request,timeout=5)
    html = response.read()
    soup = BeautifulSoup(html)
    div  = soup.find('div',class_ = 'ly_newCon')
    introduction = ''
    for st in div.stripped_strings:
        introduction += st
    introduction = introduction.encode('utf-8')
    return introduction

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

def read_dealed():
    f = open('dealed.txt','r')
    global dealed
    for f_d in f.readlines():
        # 添加的时候去掉最后一个换行符
        dealed.append(f_d[0:-1])
if __name__ == '__main__':
    read_dealed()
    addPage()
    # getLawyer('http://lawyer.9ask.cn/library/lists-2-0-0-0-0-0-14.html')