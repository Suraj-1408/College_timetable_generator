from  flask import Flask,render_template
from flask_mysqldb import MySQL
from student import student_blp

app = Flask(__name__,template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='P@swan3441'
app.config['MYSQL_DB'] = 'college_schedule'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.secret_key = 'sadsmdsdeopmas'  # Necessary for session management


student_blp.mysql = mysql

app.register_blueprint(student_blp,url_prefix='/student')

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



if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)