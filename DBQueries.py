import json
import pyodbc

config = json.load(open('config.json'))
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                      + config['db_server_name'] + ';DATABASE=TokenTest;UID='
                      + config['db_user'] + ';PWD' + '=' + config['db_pass'])
cursor = conn.cursor()


def add_token(token, verified, passed, honeypot, network, exchange):
    print('adding token to db')
    cursor.execute('INSERT INTO Tokens (address, passed, verified, honeypot, network, dateadded, exchange) ' +
                   'VALUES (?, ?, ?, ?, ?, GETDATE(), ?)',
                   token, passed, verified, honeypot, network, exchange)
    conn.commit()
