from flask import render_template,Blueprint,request,redirect,url_for
from ..models import mysqldb
import hashlib
from ..views import login
from .data import data
admin = Blueprint('admin', __name__, url_prefix='/admin')
# conn=pymysql.connect(host='localhost',user='root',password='',db='myproject')
mysql = mysqldb

@admin.route('',methods=['GET'])
def adminpage():
    return render_template('admin.html.jinja')

@admin.route('/admin_user',methods=['GET'])
def adminpage_user():
    with mysql.connection.cursor() as cur:
        cur.execute("SELECT * FROM users")
        data = cur.fetchall()
    return render_template('admin_user.html.jinja',data=data)

@admin.route('/admin_sensor',methods=['GET'])
def adminpage_sensor():
    with mysql.connection.cursor() as cur:
        cur.execute("SELECT * FROM sensor")
        data = cur.fetchall()
    return render_template('admin_sensor.html.jinja',data=data)


@admin.route('/admin_add',methods=['GET'])
def adminpage_add():
    return render_template('admin_add.html.jinja')

@admin.route('/admin_add_s',methods=['GET'])
def adminpage_add_s():
    return render_template('admin_sensor_add.html.jinja')

@admin.route('/edit',methods=['POST'])
def edit():
    if request.method == 'POST':
        Id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        with mysql.connection.cursor() as cur:
            sql = "update users set username = %s , email = %s , role = %s where Id = %s"
            cur.execute(sql,(username,email,role,Id))
            mysql.connection.commit()
        return redirect('admin_user')
    return render_template('admin_edit.html.jinja')

@admin.route("/insert", methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        username = name
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        if cpassword == password:
            
            # password = 'pa$$w0rd'
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            # print(h.hexdigest())
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            mycursor = mysql.connection.cursor()
            sql = "INSERT INTO users (username, name, email, password) VALUES (%s, %s, %s, %s)"
            val = (email, name, email, hashed_password)
            mycursor.execute(sql, val)
            mysql.connection.commit()
            mycursor.close()
            return redirect(url_for('admin.adminpage_user'))
        else:
            return redirect(url_for('admin.adminpage_user'))

@admin.route('/delete/<string:id>',methods=['GET'])
def delete(id):
    id=id
    with mysql.connection.cursor() as cur:
        sql = "DELETE FROM users WHERE Id = %s"
        cur.execute(sql, (id,))
        mysql.connection.commit()
    return redirect(url_for('admin.adminpage_user')) 


@admin.route('/admin_home',methods=['GET'])
def adminpage_home():
    return render_template('admin_home.html.jinja')



@admin.route('/editsensor',methods=['POST'])
def editsensor():
    if request.method == 'POST':
        Id = request.form['id']
        node_name = request.form['node_name']
        with mysql.connection.cursor() as cur:
            sql = "update sensor set node_name = %s where Id = %s"
            cur.execute(sql,(node_name,Id))
            mysql.connection.commit()
        return redirect('admin_sensor')
    return render_template('admin_edit.html.jinja')

@admin.route("/insert_sensor", methods=['POST'])
@admin.route("/insert_sensor", methods=['POST'])
def insert_sensor():
    data()
    if request.method == 'POST':
        node_name = request.form['node_name']
        userId = request.form['user_id']  

        password = request.form['password']
        username = request.form['username']
        role = request.form['role']
        userdata = (userId,username,password,role)

        mycursor = mysql.connection.cursor()

        mycursor.execute("SELECT * FROM sensor WHERE node_name = %s AND user_id = %s", (node_name, userId))
        existing_sensor = mycursor.fetchone()  # ดึงข้อมูลเซนเซอร์ที่มีอยู่

        if existing_sensor:
            mycursor = mysql.connection.cursor()
            with mysql.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM all_sensor")
                all_sensor = cursor.fetchall()
        
                mycursor.execute("SELECT * FROM sensor WHERE user_id = %s", (userId,))
                sensor = mycursor.fetchall()
                mycursor.close() 

            with mysql.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (userId,))
                fire_location = cursor.fetchall()

        else:
            mycursor = mysql.connection.cursor()
            with mysql.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM all_sensor")
                all_sensor = cursor.fetchall()
        
                sql = "INSERT INTO sensor (node_name, user_id) VALUES (%s, %s)"
                val = (node_name, userId)  
                mycursor.execute(sql, val) 
                mysql.connection.commit()  
                mycursor.execute("SELECT * FROM sensor WHERE user_id = %s", (userId,))
                sensor = mycursor.fetchall()
                mycursor.close()  
        
            with mysql.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (userId,))
                fire_location = cursor.fetchall()

        return render_template('map.html.jinja', data=sensor,datauser=userdata,allsensor=all_sensor,fire_location=fire_location)

    else:
        return "Error: Invalid request method"

@admin.route('/deletess',methods=['POST'])
def deletess():
    data()
    id = request.form['id']
    userId = request.form['user_id'] 
    password = request.form['password']
    username = request.form['username']
    role = request.form['role']
    userdata = (userId,username,password,role)
    with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM all_sensor")
            all_sensor = cursor.fetchall()
    with mysql.connection.cursor() as cur:
            sql = "DELETE FROM sensor WHERE Id = %s"
            cur.execute(sql, (id,)) 
            mysql.connection.commit()
    mycursor = mysql.connection.cursor()
    mycursor.execute("SELECT * FROM sensor WHERE user_id = %s", (userId,))
    sensor = mycursor.fetchall()
    mycursor.close()
    with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (userId,))
            fire_location = cursor.fetchall()
    return render_template('map.html.jinja', data=sensor,datauser=userdata,allsensor=all_sensor,fire_location=fire_location)

@admin.route('/edit_sensor',methods=['POST'])
def edit_sensor():
    data()
    Id = request.form['id']
    userId = request.form['user_id'] 
    password = request.form['password']
    username = request.form['username']
    role = request.form['role']
    node_name = request.form['node_name']
    userdata = (userId,username,password,role)
    with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM all_sensor")
            all_sensor = cursor.fetchall()
    with mysql.connection.cursor() as cur:
            sql = "update sensor set node_name = %s where Id = %s"
            cur.execute(sql,(node_name,Id))
            mysql.connection.commit()
    mycursor = mysql.connection.cursor()
    mycursor.execute("SELECT * FROM sensor WHERE user_id = %s", (userId,))
    sensor = mycursor.fetchall()
    mycursor.close()
    with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (userId,))
            fire_location = cursor.fetchall()
    return render_template('map.html.jinja', data=sensor,datauser=userdata,allsensor=all_sensor,fire_location=fire_location)