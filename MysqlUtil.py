import mysql.connector
import traceback

class MysqlUtil():
    db = {}

    def __init__(self, dns):
        self.db = self.connect(dns)

    def connect(self, dns):
        db = mysql.connector.connect(host=dns['host'], user=dns['user'], passwd=dns['pwd'], database=dns['db'])
        return db

    def createTb(self, tableName):
        sql = "drop table if exists %s" % (tableName)
        self.runSql(self, sql)

    def insertTb(self, tableName,keys,vals):
        sql ="INSERT INTO " + tableName + "("+keys+") VALUES ("+vals+")"
        # print(sql)
        result = self.runSql(sql, False)
        return result

    def updateTb(self, tableName, sets,where):
        sql = "UPDATE " + tableName + " SET " + sets+" "+where
        # print(sql)
        result = self.runSql(sql,False)
        return result

    def selectTb(self, tableName, where):
        sql = "SELECT * FROM " + tableName + " WHERE " + where
        # print(sql)
        result = self.runSql(sql)
        return result

    def runSql(self, sql,isFetch=True):
        # 使用cursor() 方法创建一个游标对象 cursor
        mycursor = self.db.cursor(dictionary=True)

        try:
            # mycursor.execute(sql, val)
            mycursor.execute(sql)
            if(isFetch):
                myresult = mycursor.fetchall()
            else:
                myresult=True
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
