DB_CONFIG = {
    'host': '39.97.34.225',
    'user': 'app_user',
    'password': 'hz543866',
    'port': 3306,
    'charset': 'utf8mb4',
    'database': 'xhs_data'
}

'''
claude mcp add mcp_server_mysql ^
  -e MYSQL_HOST="39.97.34.225" ^
  -e MYSQL_PORT="3306" ^
  -e MYSQL_USER="app_user" ^
  -e MYSQL_PASS="hz543866" ^
  -e MYSQL_DB="your_database" ^
  -e ALLOW_INSERT_OPERATION="true" ^
  -e ALLOW_UPDATE_OPERATION="true" ^
  -e ALLOW_DELETE_OPERATION="true" ^
  -- npx @benborla29/mcp-server-mysql

'''