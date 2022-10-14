import json
import requests
import time
import mysql.connector
import traceback

def getIp():
    # iplist get agent ip
    ip_url = 'http://api.tianqiip.com/getip'
    res = requests.get(ip_url)
    print(res.text)
    ip_json = json.loads(res.text)

    ip = 0
    if ip_json['code'] == 1000:
        ip = ip_json['data'][0]['ip'] + ":" + str(ip_json['data'][0]['port'])
    return ip


def getHead(request_length):
    return {"Content-Type": "application/json", "Content-Length": str(request_length),
            "Host": "gateway.jiangongdata.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Accept": "*/*", "Connection": "keep-alive"}


def postUrl(post_url, post_json, head_str, proxy):
    requests.packages.urllib3.disable_warnings()
    r = requests.post(post_url, post_json, headers=head_str,
                      verify=False, proxies=proxy)
    return r.text

def parse_json(jstr, post_json):
    job = json.loads(jstr)
    # print(job['status'])
    if (job['status']):
        jlen = len(job['data']['records'])
        for jl in range(jlen):
            print('For--'+str(jl)+'--')
            # print(job['data']['records'][jl])
            into_table(job['data']['records'][jl], post_json)
            # break
def into_table(arr, post_json):
    # print(arr)
    # print(arr['name'])
    myresult = sele_table(arr)
    # print(myresult)
    if myresult is None:
        print(arr['name'], ' 不存在！')
        insert_table(arr, post_json)
    else:
        print(arr['name'], ' 已经存在！')
        update_table(arr, post_json)
     
def insert_table(arr, post_json):
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="", database="db")
    mycursor = mydb.cursor()
    # sql = "INSERT INTO company_list (company_id, company_name,search_json,) VALUES (%s, %s,)"
    # val = [arr['cid'], arr['name']]    
    sql = "INSERT INTO company_list(company_id,company_name,search_json,from_page,create_at,status,content) \
       VALUES ('%s', '%s', '%s','%d','%d','%d','%s')" % \
       (arr['cid'], arr['name'],json.dumps(json.loads(post_json)),p,time.time(),1,json.dumps(arr))
    try:
        # mycursor.execute(sql, val)
        mycursor.execute(sql)
        mydb.commit()
        # print(arr['name'],mycursor.rowcount,"记录插入成功。")
        print("1 条记录已插入, ID:", mycursor.lastrowid)
    except:
        # 输出异常信息
        traceback.print_exc()
        # 如果发生异常，则回滚
        mydb.rollback()
    finally:
        # 最终关闭数据库连接
        mydb.close()


def update_table(arr, post_json):
    # print(arr)
    print(arr['name'])
    # print(arr['estiblishTime'])
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="", database="db")
    mycursor = mydb.cursor()
    sql = "UPDATE company_list SET search_json = '"+json.dumps(json.loads(post_json))+"',create_at= "+str(time.time())+",status= 1,content= '"+json.dumps(arr)+"' WHERE company_name = '" + \
        arr['name']+"'"

    try:
        # mycursor.execute(sql, val)
        mycursor.execute(sql)
        mydb.commit()
        # print(mycursor.rowcount, " 条记录被修改")
        print("1 条记录已更新 ID:", mycursor.lastrowid)
    except:
        # 输出异常信息
        traceback.print_exc()
        # 如果发生异常，则回滚
        mydb.rollback()
    finally:
        # 最终关闭数据库连接
        mydb.close()


def sele_table(arr):
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="", database="db")
    mycursor = mydb.cursor()
    sql = "SELECT * FROM company_list WHERE company_name='"+arr['name']+"'"

    try:
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        # print(myresult)
    except:
        # 输出异常信息
        traceback.print_exc()
        # 如果发生异常，则回滚
        mydb.rollback()
    finally:
        # 最终关闭数据库连接
        mydb.close()
    return myresult

if __name__:
    test_url = 'http://httpbin.org/post'

    ip_add = 'http://' + getIp()
    now = time.localtime(time.time())
    print(time.strftime("%Y-%m-%d %H:%M:%S", now))
    proxies = {
        "http": ip_add
    }
    data = '{"pageNum":1}'
    json_len = len(data)
    head_str = getHead(json_len)

    res = postUrl(test_url, data, head_str, proxies)
    re_arr = parse_json(res, data)
    # print(res)
