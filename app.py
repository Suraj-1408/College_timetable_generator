from  flask import Flask,render_template
from flask_mysqldb import MySQL
#from models import create_tables

app = Flask(__name__,template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='P@swan3441'
app.config['MYSQL_DB'] = 'college_schedule'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Call create_tables during application initialization
#create_tables()

app.secret_key = 'sadsmdsdeopmas'  # Necessary for session management


def register_blueprints(app):
        from student import student_blp
        from professor import professor_blp
        from admin import admin_blp
        from timetable import timetable_blp


        # Attach the MySQL instance to the blueprint
        student_blp.mysql = mysql
        professor_blp.mysql = mysql
        admin_blp.mysql = mysql
        timetable_blp.mysql = mysql


        app.register_blueprint(student_blp,url_prefix='/student')
        app.register_blueprint(professor_blp,url_prefix='/professor')
        app.register_blueprint(admin_blp,url_prefix='/admin')
        app.register_blueprint(timetable_blp,url_prefix='/timetable')

register_blueprints(app)


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)