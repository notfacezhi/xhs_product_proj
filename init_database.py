import pymysql

conn = pymysql.connect(
    host="39.97.34.225",
    user="app_user",
    password="hz543866",
    port=3306,
    charset="utf8mb4"
)

cursor = conn.cursor()

with open('create_table.sql', 'r', encoding='utf-8') as f:
    sql_commands = f.read().split(';')
    for command in sql_commands:
        command = command.strip()
        if command:
            cursor.execute(command)
            conn.commit()
 
print("数据库和表创建成功!")

cursor.close()
conn.close()
