SECRET_KEY = ""
# DATABASE_CONFIG = 'mysql://T20-F:NFM2XffD5BG25BKj@127.0.0.1/T20-F' #mysql://用户名:密码@数据库地址/要连接的数据库
userpass = 'mysql+pymysql://root:@'
basedir = '127.0.0.1'
dbname = '/T20-F'
socket = '?unix_socket=/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
dbname = dbname + socket
DATABASE_CONFIG = userpass + basedir + dbname
