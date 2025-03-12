from flask import render_template,Blueprint
from .data import data
home = Blueprint('home',__name__,url_prefix='/')

@home.route('',methods=['GET'])
def homepage():
    
    return render_template('home.html.jinja')

@home.route('/about',methods=['GET'])
def about():
    print('jaaa')
    return 'okk',200