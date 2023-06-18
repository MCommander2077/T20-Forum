import os
import ast
import platform

from flask import (Flask, Response, make_response, redirect, render_template,
                    request, url_for, session, jsonify)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

import threading

# f'''{self.artist_song}|*|{self.geneticist}|*|{self.difficult}|*|{self.video}|*|{self.download_url}|*|{self.song_id}'''

# 定义全局变量
data = ''
password = config.SECRET_KEY

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'secret_key')

app.config['SECRET_KEY'] = (os.urandom(24))

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 绑定Flask对象
db = SQLAlchemy(app)


class DatasTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.String(512))

    def __repr__(self):
        return f'{self.data}|*|{self.id}'


def db_get_data(id):
    try:
        data = DatasTable().query.filter_by(id=id).all()[0]
    except Exception as error:
        return False
    return str(data)


def db_get_all_data():
    users = DatasTable().query.all()
    data=[]
    for i in range(len(users)):
        data.append(str(users[i]))
    return data


with app.app_context():
    db.create_all()


class MyForm(FlaskForm):
    name = StringField('曲师+歌曲/Artist+Song:')
    geneticist = StringField('谱师/Geneticist:')
    difficult = StringField('难度/Difficult:')
    video = StringField('视频/Vidio:')
    downloadURL = StringField('下载链接/DownloadURL:')
    submit = SubmitField('提交/Submit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/levels')
def levels():
    # 默认显示第一页
    page = 1
    # 检查请求参数中的 page 值
    if 'page' in request.args:
        page = int(request.args['page'])
        if page <= 1:
            page = 1
            pagelist = [1, 1, 2]
        else:
            pagelist = [(page - 1), page, (page + 1)]
    else:
        page = 1
        pagelist = [1, 1, 2]

    try:
        idata = db_get_all_data()
        if not idata:
            error = "No Data Has Found"
            return render_template('404.html', error=error), 404  # 返回模板和状态码
        final_data = []
        for i in range(len(idata)):
            final_data.append(idata[i].strip().split('|*|'))

    except Exception as error:
        return render_template('404.html', error=error), 404  # 返回模板和状态码
    return render_template('list.html', data=final_data[((page - 1) * 10):(page * 10)], pagelist=pagelist)


@app.route('/admin-login')
def login_static():
    return render_template('login.html')


@app.route('/admin-login', methods=['POST'])
def login_post():
    global password  # 声明全局变量'
    form = MyForm()
    pwd = request.form['password']  # 获取用户提交的密码

    if pwd == password:  # 判断密码是否正确
        resp = make_response('<meta http-equiv="Refresh" content="0;url=../admin" />')  # 使用表单渲染模板
        session['password'] = pwd  # 将密码存储在cookie中
        return resp
    else:
        return render_template('login.html', error='密码错误')


@app.route('/song/<int:song_id>')
def get_song(song_id):
    result = db_get_data(song_id)
    if not result:
        pass
    elif str(result):
        return render_template('songinfo.html', item=result.strip().split('|*|'))
    else:
        pass
    return render_template('404.html', error='Song Not Found'), 404  # 返回模板和状态码


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pwd_cookie = session.get('password')  # 获取密码cookie
    pwd = pwd_cookie if pwd_cookie else ''  # 如果cookie不存在，初始化密码为空

    form = MyForm()

    if pwd == password:  # 如果密码正确，则返回内容
        pass
    elif pwd == '':
        return '''
<script>
function myFunction()
{alert("未登录！");}
myFunction()
</script>
<meta http-equiv="Refresh" content="0;url=../admin-login" />
'''  # 否则重定向至登录页面
    else:
        return '''
<script>
function myFunction()
{alert("密码错误！");}
myFunction()
</script>
<meta http-equiv="Refresh" content="0;url=../admin-login" />
'''  # 否则重定向至登录页面

    if form.validate_on_submit():
        if form.name.data and form.difficult.data and form.video.data and form.downloadURL.data and form.geneticist.data:
            # 创建新的数据行
            new_data = DatasTable(
                data=f"{form.name.data}|*|{form.difficult.data}|*|{form.video.data}|*|{form.downloadURL.data}|*|{form.geneticist.data}"
            )
            # 添加到数据库
            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return '''
<script>
function myFunction()
{alert("不能提交空值！");}
myFunction()
</script>
<meta http-equiv="Refresh" content="0" />
'''
    return render_template('admin.html', form=form)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html', error=e), 404  # 返回模板和状态码


if __name__ == '__main__':
    #app.run(debug=True, host='127.0.0.1', port=9807)
    app.run(host='127.0.0.1', port=9800)
