from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for,session,current_app
import MySQLdb.cursors
import re

from models import add_professor, get_all_professors, add_course, get_all_courses,add_lecture,add_classroom,get_all_classrooms,get_all_lectures,generate_valid_timetables

from forms import AddProfessorForm, AddCourseForm,AddLectureForm,AddClassroomForm
from datetime import datetime
#from timetable import generate_timetable,download_timetable

admin_blp = Blueprint('admin',__name__,static_folder='static',template_folder='templates/admin')


@admin_blp.route('/')
def dashboard():
    return render_template('admin_dashboard.html')


@admin_blp.route('/admin_login',methods = ['GET','POST'])
def admin_login():
    mesage = ''
    mysql = admin_blp.mysql  # Access the MySQL instance
    
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form :
        email = request.form['email']
        password = request.form['password']
        #mysql = current_app.extensions['mysql']
        #if not mysql:
         #   return "MySQL not initialized", 500
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email,password,))
        admin = cursor.fetchone()

        if admin:
            session['loggedin'] = True
            session['adm_id'] = admin['adm_id']
            session['admin_name'] = admin['admin_name']
            session['email'] = admin['email']
            session['password']= admin['password']
                
            mesage = 'Logged in Successfully !'
        
            return render_template('admin_dashboard.html',mesage = mesage)

        else:
            mesage = 'Kindly enter correct email & password'

    elif request.method == 'POST':
        mesage = 'Fill all inputs for login'
    
    return render_template('admin_login.html',mesage = mesage)


@admin_blp.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('adm_id',None)
    session.pop('email',None)
    
    #return redirect(url_for('student_login'))
    return render_template('admin_login.html')


@admin_blp.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    message = ''
    mysql = admin_blp.mysql  # Access the MySQL instance
    
    if request.method == 'POST' and 'admin_name' in request.form and 'email' in request.form and 'password' in request.form:
        admin_name = request.form['admin_name']
        email = request.form['email']
        password = request.form['password']

        # Execute create table query if the table doesn't exist
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SHOW TABLES LIKE "admin"')
        result = cursor.fetchone()

        if not result:
            create_query = '''
            CREATE TABLE admin (
                adm_id INT AUTO_INCREMENT PRIMARY KEY,
                admin_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            '''       
            cursor.execute(create_query)
            mysql.connection.commit()

        # Check if professor email already exists
        cursor.execute('SELECT * FROM admin WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            message = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid Email'
        elif not admin_name or not email or not password:
            message = 'Please fill out the form completely'
        else:
            # Insert professor data into the table
            cursor.execute('INSERT INTO admin (admin_name, email, password) VALUES (%s, %s, %s)', (admin_name, email, password))
            mysql.connection.commit()
            message = 'You have successfully registered'

        #cursor.close()
        return render_template('admin_register.html', message=message)

    elif request.method == 'POST':
        message = 'Please fill out the form'

    return render_template('admin_register.html', message=message)


#Function to handle add new professor details.
@admin_blp.route('/add_professor', methods=['GET', 'POST'])
def add_professor_view():
    form = AddProfessorForm()
    if form.validate_on_submit():
        professor_id = form.professor_id.data
        name = form.name.data
        add_professor(professor_id, name)
        flash('Professor added successfully!', 'success')
        return render_template('add_professor.html', form=form)

    return render_template('add_professor.html', form=form)




@admin_blp.route('/add_course', methods=['GET', 'POST'])
def add_course_view():
    form = AddCourseForm()

    # Fetch professors from the database
    mysql = admin_blp.mysql  # Access the MySQL instance
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT professor_id, name FROM professors")
    professors = cursor.fetchall()
    cursor.close()

    # Populate the professors field
    form.professors.choices = [(professor['professor_id'], professor['name']) for professor in professors]

    if form.validate_on_submit():
        course_number = form.course_number.data
        course_name = form.course_name.data
        max_numb_students = form.max_numb_students.data
        selected_professors = form.professors.data

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO courses (course_number, course_name, max_numb_students) VALUES (%s, %s, %s)",
            (course_number, course_name, max_numb_students)
        )
        mysql.connection.commit()

        # Retrieve the course_id of the newly added course
        cursor.execute("SELECT course_id FROM courses WHERE course_number = %s", (course_number,))
        course_id = cursor.fetchone()['course_id']

        # Insert into course_professor table
        for professor_id in selected_professors:
            cursor.execute(
                "INSERT INTO course_professor (course_id, professor_id) VALUES (%s, %s)",
                (course_id, professor_id)
            )

        mysql.connection.commit()
        cursor.close()

        flash('Course added successfully!', 'success')
       #return redirect(url_for('admin.add_course_view'))
        return render_template('add_course.html', form=form)
        
    return render_template('add_course.html', form=form)



@admin_blp.route('/professors')
def list_professors():
    mysql = admin_blp.mysql  # Access the MySQL instance
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch professors from the database
    cursor.execute("SELECT professor_id, name FROM professors")
    professors = cursor.fetchall()

    cursor.close()

    #professors = get_all_professors()
    return render_template('professors.html', professors=professors)

@admin_blp.route('/courses')
def list_courses():
    courses = get_all_courses()
    return render_template('courses.html', courses=courses)



@admin_blp.route('/add_lecture', methods=['GET', 'POST'])
def add_lecture_view():
    form = AddLectureForm()

    # Fetch courses from the database
    courses = get_all_courses()
    classrooms = get_all_classrooms()



    # Populate the courses field
    form.course.choices = [(course['course_id'], course['course_name']) for course in courses]
    form.classroom.choices = [(classroom['classroom_id'], classroom['classroom_name']) for classroom in classrooms]

    if form.validate_on_submit():
        course_id = form.course.data
        classroom_id = form.classroom.data
        time_slot = form.time.data
        day_of_week = form.day_of_week.data

        '''
        # Insert the lecture into the database
        add_lecture(course_id, time_slot, day)

        flash('Lecture scheduled successfully!', 'success')
        return render_template('add_lecture.html', form=form)
        '''
      
      # Check if there's a lecture scheduled for the same time and day
        if clash(classroom_id,time_slot, day_of_week):
            flash('Another lecture is already scheduled at this time.', 'error')
        else:
            # Insert the lecture into the database
            add_lecture(course_id,classroom_id, time_slot, day_of_week)
            flash('Lecture scheduled successfully!', 'success')
            return render_template('add_lecture.html', form=form)

    return render_template('add_lecture.html', form=form)




def clash(classroom_id,time_slot, day_of_week):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()

    # Convert the time slot to datetime objects for comparison
    time_start, time_end = time_slot.split(' - ')
    start_time = datetime.strptime(time_start, '%H:%M')
    end_time = datetime.strptime(time_end, '%H:%M')

    # Fetch existing lectures for the same day
    query = """
    SELECT time_slot
    FROM lectures
    WHERE classroom_id =  %s and day_of_week = %s
    """
    cursor.execute(query, (classroom_id,day_of_week,))
    existing_lectures = cursor.fetchall()

    # Check if the new lecture clashes with any existing lecture
    for lecture in existing_lectures:
        existing_start, existing_end = lecture['time_slot'].split(' - ')
        existing_start_time = datetime.strptime(existing_start, '%H:%M')
        existing_end_time = datetime.strptime(existing_end, '%H:%M')
        if (existing_start_time <= start_time < existing_end_time) or \
           (existing_start_time < end_time <= existing_end_time) or \
           (start_time <= existing_start_time and end_time >= existing_end_time):
            return True

    return False


@admin_blp.route('/lectures')
def list_lectures():
    lectures = get_all_lectures()
    return render_template('lectures.html', lectures=lectures)



@admin_blp.route('/add_classroom',methods=['GET','POST'])
def add_classroom_view():
    form = AddClassroomForm()

    if form.validate_on_submit():
        classroom_name = form.classroom_name.data
        classroom_capacity = form.classroom_capacity.data
        add_classroom(classroom_name,classroom_capacity)
        flash('ClassRoom added Sucessfully !','success')
        return render_template('add_classroom.html',form=form)

    return render_template('add_classroom.html',form=form)


def add_classroom(classroom_name,classroom_capacity):
    mysql=admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "Insert into classrooms (classroom_name,classroom_capacity) values (%s,%s)"
    cursor.execute(query,(classroom_name,classroom_capacity))
    conn.commit()
    cursor.close()



@admin_blp.route('/classrooms')
def list_classrooms():
    classrooms = get_all_classrooms()
    return render_template('classrooms.html', classrooms=classrooms)


@admin_blp.route('/delete_classroom/<int:classroom_id>', methods = ['POST'])
def delete_classroom(classroom_id):
    delete_classroom_by_id(classroom_id)
    flash('Classroom deleted Sucessfully!','succes')
    #return render_template('classrooms.html')
    return redirect(url_for('admin.list_classrooms'))  # Redirect to classrooms page after deletion


def delete_classroom_by_id(classroom_id):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "Delete from classrooms where classroom_id= %s"
    cursor.execute(query,(classroom_id,))
    conn.commit()
    cursor.close()


  
