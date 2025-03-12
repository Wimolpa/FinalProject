from flask import render_template,Blueprint,redirect,request,url_for
from flask_mysqldb import MySQL
import hashlib

from ..models import mysqldb

register = Blueprint('register',__name__,url_prefix='/register')

mysql = mysqldb



@register.route('',methods=['GET'])
def registerpage():
    return render_template('register.html.jinja')

@register.route('/about',methods=['GET'])
def about():
    print('jaaa')
    return 'okk',200

@register.route("/insert", methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = email
        password = request.form['password']
        cpassword = request.form['cpassword']

        mycursor = mysql.connection.cursor()
        sql = "SELECT * FROM users WHERE email = %s"
        user = mycursor.execute(sql, (email,))
        mysql.connection.commit()
        print('USER ',user)
        if user:
            return redirect(url_for('register.registerpage'))

        if cpassword == password:
            
            # password = 'pa$$w0rd'
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            # print(h.hexdigest())
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            sql = "INSERT INTO users (username, name, email, password) VALUES (%s, %s, %s, %s)"
            val = (username, name, email, hashed_password)
            mycursor.execute(sql, val)
            mysql.connection.commit()
            mycursor.close()
            return redirect(url_for('cregister.cregisterpage'))
        else:
            return redirect(url_for('register.registerpage'))
    