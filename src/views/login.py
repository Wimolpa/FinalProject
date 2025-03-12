from flask import render_template, Blueprint, redirect, request, url_for, flash,session
import pymysql
from ..views import map
from ..models import mysqldb
from .data import data
login = Blueprint('login', __name__, url_prefix='/login')
# conn = pymysql.connect(host='localhost', user='root', password='', db='myproject')
import hashlib
from .map import position

# app = Flask(__name__)
mysql = mysqldb



def calculate_position(id):
    sensor = []
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM sensor WHERE user_id = %s", (id,))
        sensor = cursor.fetchall()
        pm25_1 = sensor[0][4] 
        pm25_2 = sensor[1][4] 
        latA, lonA =None, None
        latB, lonB =None, None
        wd = None
        ws = None
        t = None
        if len(sensor) == 0:
            return 'ไม่พบข้อมูล'
        else:
            if pm25_1 > 80.0:
                latA, lonA = sensor[0][2], sensor[0][3]
                latB, lonB = sensor[1][2], sensor[1][3]
                wd = sensor[0][5]
                ws = sensor[0][6]
                t = sensor[0][8]
            if pm25_2 > 80.0:
                latA, lonA = sensor[1][2], sensor[1][3]
                latB, lonB = sensor[0][2], sensor[0][3]
                wd = sensor[1][5]
                ws = sensor[1][6]
                t = sensor[1][8]
            # latA, lonA =    16.872216,99.125133
            # latB, lonB =  16.813103,99.189531
            # ws = 3.9829# ความเร็วลม กม./ชม.
            # wd = 0 # ทิศทางลม องศา
            # t ='0.0'
            latC, lonC  = position(latA, lonA, latB, lonB,wd,ws,t)
            print( latC, lonC )
    return latC, lonC ,t

@login.route('', methods=['GET'])
def loginpage():
    return render_template('login.html.jinja')

@login.route('/about', methods=['GET'])
def about():
    print('jaaa')
    return 'okk', 200

@login.route("/login_user", methods=['POST'])
def login_route():
    data()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sensor = []
        fire_location = []
        # ใช้ with statement เพื่อเปิด cursor
        with mysql.connection.cursor() as cursor:
            # Query เพื่อดึง username, password และ role ของผู้ใช้
            cursor.execute("SELECT Id, username, password, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM all_sensor")
            all_sensor = cursor.fetchall()
        
            
            if user:
                print('user:', user)
                hashed_password = user[2]
                role = user[3]  
                id = user[0]

                # เข้ารหัส password ที่กรอกมา
                password_hashed = hashlib.md5(password.encode()).hexdigest()

                
                # ตรวจสอบว่า password ที่เข้ารหัสตรงกับข้อมูลในฐานข้อมูลหรือไม่
                if hashed_password == password_hashed:
                    print('pass', hashed_password, password_hashed)
                    
                    # เก็บข้อมูลผู้ใช้ใน session
                    session['username'] = username
                    session['role'] = role  
                    
                    # ตรวจสอบ role และเปลี่ยนเส้นทางไปยังหน้าตาม role ของผู้ใช้
                    if role == 'admin':
                        return redirect(url_for('admin.adminpage_user'))  
                    elif role == 'user':

                            with mysql.connection.cursor() as cursor:
                    # ลบข้อมูลทั้งหมดในตาราง fire_location ตาม user_id
                                cursor.execute("DELETE FROM fire_location WHERE user_id = %s", (id,))
                                mysql.connection.commit()

                            
                            with mysql.connection.cursor() as cursor:
                                cursor.execute("SELECT * FROM sensor WHERE user_id = %s", (id,))
                                sensor = cursor.fetchall()
                                pm25_1 = sensor[0][4] 
                                pm25_2 = sensor[1][4] 
                            if pm25_1 > 80.0 or pm25_2 > 80.0:
                                latc,lonc,time =calculate_position(id)
                                with mysql.connection.cursor() as cursor:
                                    cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (id,))
                                    fire_location = cursor.fetchall()
                                    sql = "INSERT INTO fire_location (lat, lon, time, user_id) VALUES (%s, %s, %s, %s)"
                                    val = (latc, lonc, time, id)  
                                    cursor.execute(sql, val)  
                                    mysql.connection.commit()
                                    cursor.close()
                            with mysql.connection.cursor() as cursor:
                                cursor.execute("SELECT * FROM fire_location WHERE user_id = %s", (id,))
                                fire_location = cursor.fetchall()
                            # latC, lonC , distance_new , wind_direction_new 
                            # print( latC, lonC , distance_new , wind_direction_new)
                            print("user ", user[0])
                    return render_template('map.html.jinja', data=sensor,datauser=user,allsensor=all_sensor, fire_location=fire_location)  # หน้าสำหรับ user
                else: 
                    flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
                    return redirect(url_for('login.loginpage'))
            else:
                flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
                return redirect(url_for('login.loginpage'))