#__author__ = 'Administrator'
# -*- coding: utf-8 -*-
import urllib
import urllib2
from bs4 import BeautifulSoup
import bs4
import MySQLdb

con= MySQLdb.connect(host='localhost',user='root',passwd='123456',db='predict',charset='utf8')
cursor =con.cursor()

def pageList(url):
    index = 1
    while index:
        per_url = url + str(index)
        if not lawPage(per_url):
            break
        index += 1
        # if index == 193:
        #     break
        # break
def lawPage(url):
    print url
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request,timeout=5)
        html = response.read()
    except:
        return True
    soup = BeautifulSoup(html)
    tag_Node = soup.find_all('div',class_='lawyer-info clearfix')

    if len(tag_Node) == 0:
        return  False

    for tag in tag_Node:
        intro_url = str('http://www.51wf.com/')+ tag.find('div',class_='avatar-ct').find('a')['href']+str('/profile')

        infor(tag.find('div',class_='lawyer-details'), url, intro_url)

    return True


def infor( soup, url, intro_url ):

    name = ''; area = ''; carrer_id = '';
    organization = ''; office_phone = '';
    cellphone = ''; email = '';
    introduction = '';skills = '';

    name_tag = soup.find('div',class_='lawyer-name clearfix').find('a')
    name = name_tag.string.encode('utf-8')
    print name

    skills_tag = soup.find('ul',class_='clearfix')
    index = 1
    for tag in skills_tag:
        if index == 1:
            skills += tag.string.encode('utf-8')
        else:
            skills += str('、')+ tag.string.encode('utf-8')
        index += 1

    information = soup.find_all('dl',class_='info-item')
    index = 1
    for tag in information:
        if index == 2:
            try:
                organization = tag.find('dd').string.encode('utf-8')
                # print index ,organization
            except:
                pass
        elif index == 3:
            try:
                area = tag.find('dd').string.encode('utf-8')
                # print index,area
            except:
                pass
        elif index == 4:
            try:
                cellphone = tag.find('dd').string.encode('utf-8')
                # print index,cellphone
            except:
                pass
        elif index == 5:
            try:
                email = tag.find('dd').string.encode('utf-8')
                # print index,email
            except:
                pass
        index += 1
    try:
        introduction = intro(intro_url)
    except:
        pass

    faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei = fingWords(introduction)
    infor_source = url.encode('utf-8')

    sql = '''insert into new_law2_copy(name,area,career_id,organization,office_phone,cellphone,email,skill,
            introduction,faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei,infor_source) values
            ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(name,
            area,carrer_id,organization,office_phone,cellphone,email,skills,introduction,faguan,fayuan,
            jianchaguan,jianchayuan,gongan,zhengfawei,infor_source)

    # print sql
    insertData(sql)

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


def intro(url):
    introduction = ''
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request,timeout=5)
        html = response.read()
    except:
        return introduction
    soup = BeautifulSoup(html)
    infor_Node = soup.find('pre',class_='text-content')
    for str in infor_Node.stripped_strings:
        introduction += str
    introduction = introduction.encode('utf-8')

    return introduction

if __name__ == '__main__':
    pageList('http://www.51wf.com/lawyers/browse--page-')