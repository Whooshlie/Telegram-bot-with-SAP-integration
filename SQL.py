import decimal
from hdbcli import dbapi
import re
import pyodbc

ADDRESS = "IPADRESSSHERE"
USER = "USERNAME"
PASS = "PASSWORD"
def SQLCommand(command, parameter:dict):
    print(command.SQL)
    query = command.SQL
    #print(parameter)
    if command.Type == "SAP":
        conn=dbapi.connect(
            address=ADDRESS ,port=30015,user=USER,password=PASS)
        cursor=conn.cursor()
        parameterList=[]
        parameterOrder=re.findall("{[^}]*}",query)
        query=re.sub("{[^}]*}",'?',query)
        for i in parameterOrder:
            parameterList.append(parameter[i[1:-1]])
        cursor.execute(query, parameterList)
        result=[[column[0] for column in cursor.description]]
        types=[]
        count=0
        for row in cursor:
            if(count==0):
                for i in range(len(result[0])):
                    types.append(type(row[i]))
            result.append([])
            for i in row:
                if(type(i)==decimal.Decimal):
                    result[-1].append(str(round(i,2)))
                else:
                    result[-1].append(str(i))
            count+=1

        if(len(types)==0):
            for i in result[0]:
                types.append(str)

        conn.close()

        return result[0], result[1:], types

    if command.Type == "Access":
        conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};' + f'DBQ={command.path};')
        cursor = conn.cursor()
        SQL = command.SQL
        for para in parameter:
            SQL = SQL.replace("{" + para + "}", parameter[para])
            print("{" + para + "}")
        print(SQL)
        cursor.execute(SQL)
        header = [column[0] for column in cursor.description]
        row = [list(row) for row in cursor.fetchall()]
        return header, row, []



