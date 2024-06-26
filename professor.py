from flask import Flask,Blueprint,render_template,request,redirect,url_for,flash,session,current_app
from models import  get_all_professors, get_all_lectures, get_all_classrooms,add_lecture

import logging
import MySQLdb.cursors
import re

professor_blp = Blueprint('professor',__name__,static_folder='static',template_folder='templates/professor')



@professor_blp.route('/professor_login',methods = ['GET','POST'])
def professor_login():
    mesage = ''
    mysql = professor_blp.mysql  # Access the MySQL instance
    
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form :
        email = request.form['email']
        password = request.form['password']
        #mysql = current_app.extensions['mysql']
        #if not mysql:
         #   return "MySQL not initialized", 500
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM professor WHERE email = %s AND password = %s', (email,password,))
        professor = cursor.fetchone()

        if professor:
            session['loggedin'] = True
            session['p_id'] = professor['p_id']
            session['professor_name'] = professor['professor_name']
            session['email'] = professor['email']
            session['password']=professor['password']
                
            mesage = 'Logged in Successfully !'
        
            return render_template('professor_dashboard.html',mesage = mesage)

        else:
            mesage = 'Kindly enter correct email & password'

    elif request.method == 'POST':
        mesage = 'Fill all inputs for login'
    
    return render_template('professor_login.html',mesage = mesage)


@professor_blp.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('pid',None)
    session.pop('email',None)
    
    #return redirect(url_for('student_login'))
    return render_template('professor_login.html')


@professor_blp.route('/professor_register', methods=['GET', 'POST'])
def professor_register():
    message = ''
    mysql = professor_blp.mysql  # Access the MySQL instance
    
    if request.method == 'POST' and 'professor_name' in request.form and 'email' in request.form and 'password' in request.form:
        professor_name = request.form['professor_name']
        email = request.form['email']
        password = request.form['password']

        # Execute create table query if the table doesn't exist
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SHOW TABLES LIKE "professor"')
        result = cursor.fetchone()

        if not result:
            create_query = '''
            CREATE TABLE professor (
                p_id INT AUTO_INCREMENT PRIMARY KEY,
                professor_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            '''
            cursor.execute(create_query)
            mysql.connection.commit()

        # Check if professor email already exists
        cursor.execute('SELECT * FROM professor WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            message = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid Email'
        elif not professor_name or not email or not password:
            message = 'Please fill out the form completely'
        else:
            # Insert professor data into the table
            cursor.execute('INSERT INTO professor (professor_name, email, password) VALUES (%s, %s, %s)', (professor_name, email, password))
            mysql.connection.commit()
            message = 'You have successfully registered'

        cursor.close()
        return render_template('professor_register.html', message=message)

    elif request.method == 'POST':
        message = 'Please fill out the form'

    return render_template('professor_register.html', message=message)




@professor_blp.route('/')
def dashboard():
    return render_template('professor_dashboard.html')



@professor_blp.route('/generate_timetable', methods=['GET', 'POST'])
def generate_professor_timetable():
    try:
        logging.debug('Entered generate_timetable route')

        # Generate timetable combinations
        timetable, timeslots, days_of_week = generate_valid_timetables()
        logging.debug(f'Timetable: {timetable}')
        logging.debug(f'Timeslots: {timeslots}')
        logging.debug(f'Days of Week: {days_of_week}')

        # Render the generated timetable to HTML
        return render_template('regular_timetable.html', timetable=timetable, timeslots=timeslots, days_of_week=days_of_week)

    except Exception as e:
        logging.error(f'Error generating timetable: {str(e)}')
        flash(f'Error generating timetable: {str(e)}', 'danger')
        return redirect(url_for('professor.regular_timetable'))

