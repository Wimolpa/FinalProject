from flask import render_template,Blueprint


cregister = Blueprint('cregister', __name__, url_prefix='/cregister')


@cregister.route('',methods=['GET'])
def cregisterpage():
    return render_template('cregister.html.jinja')