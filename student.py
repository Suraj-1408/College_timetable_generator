from flask import Flask,Blueprint,render_template,request,redirect,url_for,session,current_app
<<<<<<< HEAD
#from flask_mysqldb import MySQL
from models import get_all_courses, get_all_professors, get_all_lectures, get_all_classrooms,   generate_valid_timetables,add_lecture

import logging
=======

from flask_mysqldb import MySQL
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
import MySQLdb.cursors
import re

student_blp = Blueprint('student',__name__,static_folder='static',template_folder='templates/student')


@student_blp.route('/student_login',methods = ['GET','POST'])
def student_login():
    mesage = ''
<<<<<<< HEAD
    mysql = student_blp.mysql  # Access the MySQL instance

=======
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
    if request.method == 'POST' and 'roll_no' in request.form and 'password' in request.form :
        roll_no = request.form['roll_no']
        password = request.form['password']
        #mysql = current_app.extensions['mysql']
        #if not mysql:
         #   return "MySQL not initialized", 500
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE roll_no = %s AND password = %s', (roll_no,password,))
        student = cursor.fetchone()

        if student:
            session['loggedin'] = True
            session['stud_id'] = student['stud_id']
            session['student_name'] = student['student_name']
            session['roll_no'] = student['roll_no']
            session['class'] = student['class']
            session['email'] = student['email']
            
            mesage = 'Logged in Successfully !'

            return render_template('student_dashboard.html',mesage = mesage)

        else:
            mesage = 'Kindly enter correct email & password'

    elif request.method == 'POST':
        mesage = 'Fill all inputs for login'
    
    return render_template('student_login.html',mesage = mesage)


@student_blp.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('stud_id',None)
    session.pop('roll_no',None)
    
<<<<<<< HEAD
    #return redirect(url_for('student_login'))
    return render_template('student_login.html')
=======
    return redirect(url_for('student_login'))
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133


@student_blp.route('/student_register',methods = ['GET','POST'])
def student_register():
    mesage = ''
<<<<<<< HEAD
    mysql = student_blp.mysql  # Access the MySQL instance

=======
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
    if request.method == 'POST' and  'student_name' in request.form and 'roll_no' in request.form and 'class' in request.form and 'email' in request.form and 'password' in request.form :

        student_name = request.form['student_name']
        roll_no = request.form['roll_no']
        standard = request.form['class']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE email = %s',(email,))

        account = cursor.fetchone()
        if account:
                mesage = 'Account Already exist '

<<<<<<< HEAD
        elif not roll_no or not standard or not email or not password:
                mesage = 'Please Fill out the form.'

        
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
                mesage = 'Invalid Email'
                
        
=======
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
                mesage = 'Invalid Email'
                
        elif not roll_no or not standard or not email or not password:
                mesage = 'Please Fill out the form.'

>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
        else:
            cursor.execute('INSERT INTO student (student_name,roll_no,class,email,password) values (%s,%s,%s,%s,%s)',(student_name,roll_no,standard,email,password))
            mysql.connection.commit()
            mesage = 'You have Successfully registered.'

<<<<<<< HEAD
        return render_template('student_register.html',mesage = mesage)
=======
        return render_template('student_login.html',mesage = mesage)
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133

    elif request.method == 'POST':
            mesage = 'Please fill out the form '
        
    return render_template('student_register.html',mesage = mesage)


<<<<<<< HEAD


@student_blp.route('/')
def dashboard():
    return render_template('student_dashboard.html')



@student_blp.route('/generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    try:
        logging.debug('Entered generate_timetable route')

        # Generate timetable combinations
        timetable, timeslots, days_of_week = generate_valid_timetables()
        logging.debug(f'Timetable: {timetable}')
        logging.debug(f'Timeslots: {timeslots}')
        logging.debug(f'Days of Week: {days_of_week}')

        # Render the generated timetable to HTML
        return render_template('Regular_timetable.html', timetable=timetable, timeslots=timeslots, days_of_week=days_of_week)

    except Exception as e:
        logging.error(f'Error generating timetable: {str(e)}')
        flash(f'Error generating timetable: {str(e)}', 'danger')
        return redirect(url_for('student.Regular_timetable'))





=======
>>>>>>> b7eacff66318ff1b9c8ad188eb0dd3fa68145133
#    if __name__ == "__main__":
#        app.debug = True
#        app.run(host='0.0.0.0', port=5000)
        