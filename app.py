from  flask import Flask,render_template
from flask_mysqldb import MySQL
<<<<<<< HEAD
#from models import create_tables
=======
from student import student_blp
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133

app = Flask(__name__,template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='P@swan3441'
app.config['MYSQL_DB'] = 'college_schedule'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

<<<<<<< HEAD
# Call create_tables during application initialization
#create_tables()
=======
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133

app.secret_key = 'sadsmdsdeopmas'  # Necessary for session management


<<<<<<< HEAD
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

=======
student_blp.mysql = mysql

app.register_blueprint(student_blp,url_prefix='/student')
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133

@app.route('/')
def home():
    return render_template('home.html')

#@app.route('/student_login',methods = ['GET','POST'])
#def student_login():
#   return render_template('student_login.html')


#@app.route('/student/student_register')
#def student_register():
#    return render_template('student_register.html')

#@app.route('/student')
#def logout():
#    return render_template('/student_login.html')

<<<<<<< HEAD
=======


>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)