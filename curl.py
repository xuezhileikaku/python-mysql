import requests
import json
import time

import mysql.connector
import traceback
import MysqlUtil


class MysqlUtil():
    db = {}

    def __init__(self, dns):
        self.db = self.connect(dns)

    def connect(self, dns):
        db = mysql.connector.connect(
            host=dns['host'], user=dns['user'], passwd=dns['pwd'], database=dns['db'])
        return db

    def createTb(self, tableName):
        sql = "drop table if exists %s" % (tableName)
        self.runSql(self, sql)

    def insertTb(self, tableName, keys, vals):
        sql = "INSERT INTO " + tableName + "("+keys+") VALUES ("+vals+")"
        # print(sql)
        result = self.runSql(sql, False)
        return result

    def updateTb(self, tableName, sets, where):
        sql = "UPDATE " + tableName + " SET " + sets+" "+where
        # print(sql)
        result = self.runSql(sql, False)
        return result

    def selectTb(self, tableName, where):
        sql = "SELECT * FROM " + tableName + " WHERE " + where
        # print(sql)
        result = self.runSql(sql)
        return result

    def runSql(self, sql, isFetch=True):
        # 使用cursor() 方法创建一个游标对象 cursor
        mycursor = self.db.cursor(dictionary=True)

        try:
            # mycursor.execute(sql, val)
            mycursor.execute(sql)
            if (isFetch):
                myresult = mycursor.fetchall()
            else:
                myresult = True
            # print(mycursor.rowcount, " 条记录被修改")
            #
            self.db.commit()
            return myresult
        except:
            # 输出异常信息
            traceback.print_exc()
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()


def getIp():
    # iplist get ip
    ip_url = 'http://api.getip.com/'

    res = requests.get(ip_url)
    print(res.text)
    ip_json = json.loads(res.text)

    ip = 0
    if ip_json['code'] == 1000:
        ip = ip_json['data'][0]['ip'] + ":" + str(ip_json['data'][0]['port'])

    return ip


def getJson(p):
    post_json = '{" "pageNum": '+p + ', "pageSize": 10}'
    return post_json


def getHead(json_len):
    head_str = {"Content-Type": "application/json", "Content-Length": str(
        json_len), "Host": "test.myip.com", "User-Agent": "PostmanRuntime/7.28.20", "Accept": "*/*", "Connection": "keep-alive"}
    return head_str


def postUrl(post_url, post_json, head_str, proxy):
    requests.packages.urllib3.disable_warnings()
    r = requests.post(post_url, post_json, headers=head_str,
                      verify=False, proxies=proxy)
    return r.text


def onePost(post_url, proxies, post_json):
    json_len = len(post_json)
    head_str = getHead(json_len)
    con_json = postUrl(post_url, post_json, head_str, proxies)
    return con_json


def parse_json(jstr, post_json, p):
    job = json.loads(jstr)
    if (job['status']):
        jlen = len(job['data']['records'])
        for jl in range(jlen):
            print('For--'+str(jl)+'--')
            into_table(job['data']['records'][jl], post_json, p)
            # break


def into_table(arr, post_json, p):
    myresult = sele_table(arr)
    re_len = len(myresult)

    if re_len > 0:
        print(arr['name'], ' 已经存在！')
        update_table(arr, post_json, p)
    else:
        print(arr['name'], ' 不存在！')
        insert_table(arr, post_json, p)


def insert_table(arr, post_json, p):
    dns = {'host': 'localhost', 'user': 'root', 'pwd': '', 'db': 'dbname'}
    mtool = MysqlUtil(dns)
    nstring = replace_none(arr)

    njstr = nstring.replace('	', '')
    narr = json.loads(njstr)

    keys = 'id,name,search_json,from_page,create_at,status,content'

    vals = "'"+narr['id']+"', '"+narr['name']+"', '"+json.dumps(json.loads(post_json), ensure_ascii=False)+"', "+str(p)+", "+str(time.time())+", 1, '" +\
        json.dumps(arr, ensure_ascii=False)+"'"

    mtool.insertTb('table', keys, vals)


def update_table(arr, post_json, p):
    arr_json = replace_none(arr)
    aob = json.loads(arr_json)
    dns = {'host': 'localhost', 'user': 'root', 'pwd': '', 'db': 'dbname'}
    mtool = MysqlUtil(dns)
    sets_str = "search_json ='" + json.dumps(json.loads(post_json), ensure_ascii=False) + "', from_page = " + str(
        p) + ",create_at= " + str(time.time()) + ",status= 1,content= '" + json.dumps(arr, ensure_ascii=False)+"'"
    # print(sets_str)
    where = "WHERE name = '" + aob['name'] + "'"
    res = mtool.updateTb('table', sets_str, where)


def sele_table(arr):
    dns = {'host': 'localhost', 'user': 'root', 'pwd': '', 'db': 'dbname'}
    mtool = MysqlUtil(dns)
    myresult = mtool.selectTb('table', "company_name='" + arr['name'] + "'")
    return myresult


def records_count(records, names):
    if records == '':
        return {'code': '', 'count': 0, 'name': ''}
    else:
        re_num = records.count(';')
        return {'code': records, 'count': re_num + 1, 'name': names}


def replace_none(arr):
    keys = list(arr.keys())
    vals = list(arr.values())

    new = '{'
    for i in range(len(arr)):
        if vals[i] is None:
            new += '"'+keys[i]+'":"",'
        else:
            if (isinstance(vals[i], str) is False):
                new += '"'+keys[i]+'":"'+str(vals[i])+'",'
            else:
                new += '"' + keys[i] + '":"' + vals[i] + '",'

    new = new[:-1]
    new += '}'
    return new


if __name__:
    test_url = 'http://httpbin.org/post'
    ip_add = 'http://'+getIp()
    now = time.localtime(time.time())
    print(time.strftime("%Y-%m-%d %H:%M:%S", now))
    proxies = {
        "http": ip_add
    }

    p = 1
    while p < 5:
        pstr = str(p)
        print("page:", pstr)
        post_json = getJson(pstr)
        # print(post_json)
        re_json = onePost(test_url, proxies, post_json)
        re_arr = parse_json(re_json, post_json, p)
        print(re_arr)
        # break
        p = p + 1
        # print(p)
        print("page+1:", p)
