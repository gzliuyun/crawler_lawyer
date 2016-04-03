#__author__ = 'Administrator'
# -*- coding: utf-8 -*-
import urllib
import urllib2
from bs4 import BeautifulSoup
import MySQLdb

con= MySQLdb.connect(host='localhost',user='root',passwd='123456',db='predict',charset='utf8')
cursor =con.cursor()
dealed = []
def readURL(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request,timeout=5)
    html = response.read()
    # print html
    soup = BeautifulSoup(html)
    list = soup.find('ul',class_ ='list')
    for i in range(len(list)):
        if str(type(list.contents[i])) == "<class 'bs4.element.Tag'>":
            addPage(list.contents[i].contents[0]['href'])

def addPage(url):
    print url
    url += '/page_'
    page = 1
    while page:
        url_page = url + str(page)
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
        return
    soup = BeautifulSoup(html)
    try:
        list = soup.find('div',class_ = 'lawer_list_content hauto')
        list = list.find_all('dl')
        if len(list) == 0:
            return False
        for per in list:
            spacify = per.find_all('a')
            try:
                infor(spacify[-2]['href'])
            except:
                continue
    except:
        return True
    return True
def infor(url):
    print url

    request = urllib2.Request(url)
    response = urllib2.urlopen(request,timeout=5)
    html = response.read()
    soup = BeautifulSoup(html)

    list  = soup.find('div',class_ = 'aside-bd aside-contact')
    if str(type(list)) == "<type 'NoneType'>":
        name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction = style2(soup)
    else :
        name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction = style1(soup,list)


    faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei = fingWords(introduction)
    infor_source = url.encode('utf-8')
    print name

    sql = '''insert into lawyers2(name,area,career_id,organization,office_phone,cellphone,email,skill,
            introduction,faguan,fayuan,jianchaguan,jianchayuan,gongan,zhengfawei,infor_source) values
            ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(name,
            area,carrer_id,organization,office_phone,cellphone,email,skills,introduction,faguan,fayuan,
            jianchaguan,jianchayuan,gongan,zhengfawei,infor_source)

    # print sql
    insertData(sql)

def style1(soup,list):
    name = ''; area = ''; carrer_id = '';
    organization = ''; office_phone = '';
    cellphone = ''; email = '';
    introduction = '';skills = '';
    for i in range(len(list)):
        li = str(list.contents[i])
        if i == 1:
            name = li[li.find('：')+len('：'):li.find('</p>')]
        if i == 3:
            carrer_id = li[li.find('：')+len('：'):li.find('</p>')]
        if i == 5:
            office_phone = li[li.find('：')+len('：'):li.find('</p>')]
        if i == 7:
            cellphone = li[li.find('：')+len('：'):li.find('</p>')]
        if i == 9:
            email = li[li.find('">')+len('">'):li.find('</a>')]
        if i == 11:
            organization = li[li.find('：')+len('：'):li.find('</p>')]
        if i == 13:
            area = li[li.find('：')+len('：'):li.find('</p>')]

    list  = soup.find('div',class_ ='main-bd main-bd-padding intro')
    tag_per = False
    tag_ser = False
    for lt in list:
        if str(lt) == '<h3>个人简介</h3>':
            tag_per = True
            continue
        elif str(lt) == '<h3>服务范围</h3>':
            tag_per = False
            tag_ser = True
            continue

        if tag_per == False and tag_ser == False:
            continue

        if tag_per == True and str(type(lt)) == "<class 'bs4.element.Tag'>":
            introduction += str(lt.text.encode('utf-8')).strip()
        if tag_ser == True and str(type(lt)) == "<class 'bs4.element.Tag'>":
            skills += str(lt.text.encode('utf-8')).strip()

    # introduction = introduction.replace('\n','')
    # # skills = skills.replace('\n','')

    return name,area,carrer_id,organization, office_phone,cellphone,email,skills,introduction

def style2(soup):
    name = ''; area = ''; carrer_id = '';
    organization = ''; office_phone = '';
    cellphone = ''; email = '';
    introduction = '';skills = '';

    list  = soup.find('div',class_ = 'inlawyer')
    st = str(list)

    name = st[st.find('</span>')+len('</span>'):st.find(' 律师')-1]

    carrer_id = st[st.find('执业证号：'):st.find('<span>办公电话')]
    carrer_id = carrer_id[carrer_id.find('</span>')+len('</span>'):carrer_id.find('<br/>')]

    office_phone = st[st.find('办公电话：'):st.find('<span>业务手机')]
    office_phone = office_phone[office_phone.find('</span>')+len('</span>'):office_phone.find('<br/>')]

    cellphone = st[st.find('业务手机：'):st.find('<span>个人网址')]
    cellphone = cellphone[cellphone.find('</span>')+len('</span>'):cellphone.find('<br/>')]

    organization = st[st.find('所属律所：'):st.find('<span>所属地区')]
    organization = organization[organization.find('</span>')+len('</span>'):organization.find('<br/>')]

    area = st[st.find('所属地区：'):-1]
    area = area[area.find('</span>')+len('</span>'):area.find('<br/>')]


    net = list.next_siblings
    index = 1
    skills = ''
    introduction = ''
    for nt in net:
        if str(type(nt)) == "<class 'bs4.element.Tag'>":
            for child in nt:
                if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                    if index == 1 :
                        skills += child.string.strip()
                    if index == 2:
                        introduction += child.string.strip()
            index += 1

    return name,area,carrer_id,organization, office_phone,cellphone,email,skills.encode('utf-8'),introduction.encode('utf-8')

def insertData(sql):
    # print sql
    try:
        cursor.execute(sql)
        con.commit()
    except:
        return

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

def crawled():
    f_dealed = open('dealed.txt','r')
    global  dealed
    for f_d in f_dealed.readlines():
        # 添加的时候去掉最后一个换行符
        dealed.append(f_d[0:-1])
    f_dealed.close()
if __name__ == '__main__':
    url = 'http://china.findlaw.cn/findlawyers/'
    crawled()
    readURL(url)
    # infor('http://liyinghongls.findlaw.cn/lawyer/onlinelawyer.html')