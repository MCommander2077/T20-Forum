import os
import platform

from flask import (Flask, Response, make_response, redirect, render_template,
                   request, url_for, session)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

import config

password = config.SECRET_KEY

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'secret_key')

app.config['SECRET_KEY'] = (os.urandom(24))

class MyForm(FlaskForm):
    name = StringField('Name:')
    difficult = StringField('Difficult:')
    video = StringField('video:')
    downloadURL = StringField('downloadURL:')
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/levels')
def levels():
    data = []
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

    with open('data.txt', 'r', encoding="GBK") as f:
        for line in f:
            data.append(line.strip().split('|*|'))
    return render_template('list.html', data=data[((page - 1) * 10):(page * 10)], pagelist=pagelist)


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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pwd_cookie = session.get('password')  # 获取密码cookie
    print(pwd_cookie)
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
        if not form.name.data == '' and not form.difficult.data == '' and not form.video.data == '' and not form.downloadURL.data == '' and not form.downloadURL.data == '':
            with open('data.txt', 'a', encoding="GBK") as f:
                f.write(f'{form.name.data}|*|{form.difficult.data}|*|{form.video.data}|*|{form.downloadURL.data}\n')
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
     app.run(debug=True,host='127.0.0.1', port=9808)
    # app.run(host='127.0.0.1', port=9809)
