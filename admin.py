from flask import Flask,flash, Blueprint, render_template, request,  redirect, url_for, session, current_app
import MySQLdb.cursors
import re

from models import add_professor,add_course,gen_msc_course_id,gen_mca_course_id,add_lecture,add_classroom,get_all_classrooms,get_all_lectures,gen_professor_id
admin_blp = Blueprint('admin', __name__, static_folder='static', template_folder='templates/admin')

from forms import AddProfessorForm,AddCourseForm,AddLectureForm,AddClassroomForm,AddMCACourseForm,UpdateClassroomForm
from timetable import create_timetables_for_program
from datetime import datetime
#from timetable import generate_timetable,download_timetable


@admin_blp.route('/')
def dashboard():
    return render_template('admin_dashboard.html')


@admin_blp.route('/admin_login',methods = ['POST','GET'])
def admin_login():
    mesage = ''
    mysql = admin_blp.mysql  # Access the MySQL instance
    
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form :
        email = request.form['email']
        password = request.form['password']
            
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
        name = form.name.data
        
        try:
            professor_id =  gen_professor_id()
            if  professor_id:
                result = add_professor(professor_id, name)
            
                if result:
                    flash(f'Professor {name} added Successfully with professor Id {professor_id}','success')
                    return redirect(url_for('admin.add_professor_view'))

                else:
                    flash(f'Professor {name} added Successfully with professor Id {professor_id}','success')

            else:
                flash('Error while generating professor Id.','danger')

        except MYSQLdb.IntegrityError as e:
            flash(f'Error: {e}','danger')
            print(f"MySQL Integrity Error:{e}")

        except Exception as e:
            flash(f'Error adding  professor:{str(e)}','danger')
            print(f"Exception in add_professor_view {e}")

    #else:
    #    flash('Error generating Professor Id, try again','danger')
    #    print("Failed to generate professor Id")
        
    return render_template('add_professor.html', form=form)


@admin_blp.route('/delete_professor/<string:professor_id>',methods=['GET','POST'])
def delete_professor(professor_id):
    delete_professor_by_id(professor_id)
    flash('Professor deleted Successfully','success')
    return redirect(url_for('admin.list_professors'))


def delete_professor_by_id(professor_id):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "Delete from professors where professor_id=%s"
    cursor.execute(query,(professor_id,))
    conn.commit()
    cursor.close()



@admin_blp.route('/update_professor/<string:professor_id>', methods=['GET', 'POST'])
def update_professor(professor_id):
    professor = get_professor_by_id(professor_id)

    form = AddProfessorForm(name=professor['name'])  # Use the same form for adding and updating

    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()

    if request.method == 'POST' and form.validate_on_submit():
        form_data = {
            'name': form.name.data
        }
        update_professor_in_db(professor_id, form_data)
        flash('Professor updated successfully', 'success')
        return redirect(url_for('admin.list_professors'))

    return render_template('update_professor.html', form=form, professor=professor)

def get_professor_by_id(professor_id):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT professor_id, name FROM professors WHERE professor_id = %s"
    cursor.execute(query,(professor_id,))
    result = cursor.fetchone()
    cursor.close()
    return result
   

def update_professor_in_db(professor_id, form_data):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "UPDATE professors SET name = %s WHERE professor_id = %s"
    cursor.execute(query, (form_data['name'], professor_id))
    conn.commit()
    cursor.close()



@admin_blp.route('/add_msc_course',methods=['GET','POST'])
def add_msc_course():
    form = AddCourseForm()

    mysql = admin_blp.mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT  name FROM professors")
    professors = cursor.fetchall()
    cursor.close()

    form.professor_name.choices = [(professor['name'], professor['name']) for professor in professors]


    if form.validate_on_submit():
        course_name = form.course_name.data
        professor_name = form.professor_name.data
        total_credits = form.total_credits.data
        no_of_lectures = form.no_of_lectures.data

        try:
            course_id = gen_msc_course_id()
            if course_id:
                cursor = mysql.connection.cursor()
                query = "Insert into msc_courses(course_id,course_name,professor_name,total_credits,no_of_lectures) values(%s,%s,%s,%s,%s)" 
                cursor.execute(query,(course_id,course_name,professor_name,total_credits,no_of_lectures))
                mysql.connection.commit()
                cursor.close()   
                flash(f'{course_name} added successfully with ID {course_id}','success')
                return redirect(url_for('admin.add_msc_course'))
                #return render_template('add_msc_course.html',form=form,course_type='MSC')

            else:
                flash(f'Course Id not generated','danger')

        except Exception as e:
            flash(f'Error while adding MSc course {e}','danger')

    return render_template('add_msc_course.html',form=form,course_type='MSC')


@admin_blp.route('/add_mca_course',methods = ['GET','POST'])
def add_mca_course():
    form = AddCourseForm()

    mysql = admin_blp.mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT  name FROM professors")
    professors = cursor.fetchall()
    cursor.close()

    form.professor_name.choices = [(professor['name'], professor['name']) for professor in professors]


    if form.validate_on_submit():
        course_name = form.course_name.data
        professor_id = form.professor_name.data
        total_credits = form.total_credits.data
        no_of_lectures = form.no_of_lectures.data

        try:
            course_id = gen_mca_course_id()
            if course_id:
                cursor = mysql.connection.cursor()
                query = "Insert into mca_courses(course_id,course_name,professor_name,total_credits,no_of_lectures) values(%s,%s,%s,%s,%s)"
                cursor.execute(query,(course_id,course_name,professor_id,total_credits,no_of_lectures))
                mysql.connection.commit()
                cursor.close()
                flash(f'{course_name } added successfully with ID {course_id}','success')
                return redirect(url_for('admin.add_mca_course'))
            
            else:
                flash('Course Id not added','danger')
            
        except Exception as e:
            flash(f'Error while adding MCA course {e}','danger')

    return render_template('add_mca_course.html',form=form,course_type='MCA')



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

@admin_blp.route('/msc_courses')
def list_msc_courses():
    mysql = admin_blp.mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("Select * from msc_courses")
    msc_courses = cursor.fetchall()
    cursor.close()

    return render_template('msc_courses.html', courses=msc_courses)

@admin_blp.route('/mca_courses')
def list_mca_courses():
    mysql = admin_blp.mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("Select * from mca_courses")
    mca_courses = cursor.fetchall()
    cursor.close()

    return render_template('mca_courses.html',courses=mca_courses)
    



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
        #classroom_name = form.classroom_name.data
        classroom_capacity = form.classroom_capacity.data
        try:
            add_classroom(classroom_capacity)
            flash('ClassRoom added Sucessfully !','success')
            return redirect(url_for('admin.add_classroom_view'))
        
        except Exception as e:
            flash(f'Error while adding classroom {e}','danger')

    return render_template('add_classroom.html',form=form)


@admin_blp.route('/classrooms')
def list_classrooms():
    classrooms = get_all_classrooms()
    return render_template('classrooms.html', classrooms=classrooms)


@admin_blp.route('/delete_classroom/<classroom_id>', methods = ['POST'])
def delete_classroom(classroom_id):
    try:
        delete_classroom_by_id(classroom_id)
        flash('Classroom deleted Sucessfully!','succes')
        #return render_template('classrooms.html')
    except Exception as e:
        flash(f'Error while deleting classroom:{e}','danger')
    return redirect(url_for('admin.list_classrooms'))  # Redirect to classrooms page after deletion


def delete_classroom_by_id(classroom_id):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "Delete from classrooms where classroom_id= %s"
    cursor.execute(query,(classroom_id,))
    conn.commit()
    cursor.close()



@admin_blp.route('/update_classroom/<classroom_id>', methods=['GET', 'POST'])
def update_classroom(classroom_id):
    form = AddClassroomForm()  # Use the same form for adding and updating

    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'GET':
        # Fetch existing classroom details to populate the form
        cursor.execute("SELECT * FROM classrooms WHERE classroom_id = %s", (classroom_id,))
        classroom = cursor.fetchone()
        cursor.close()

        if classroom:
            form.classroom_id.data = classroom['classroom_id']
            #form.classroom_name.data = classroom['classroom_name']
            form.classroom_capacity.data = classroom['classroom_capacity']
        else:
            flash('Classroom not found!', 'danger')
            return redirect(url_for('admin.list_classrooms'))

    if form.validate_on_submit():
        classroom_id = form.classroom_id.data 
        #classroom_name = form.classroom_name.data
        classroom_capacity = form.classroom_capacity.data

        cursor = conn.cursor()
        query = "UPDATE classrooms SET classroom_id = %s, classroom_capacity = %s WHERE classroom_id = %s"
        cursor.execute(query, (classroom_id,classroom_capacity,classroom_id))
        conn.commit()
        cursor.close()

        flash('Classroom updated successfully!', 'success')
        return redirect(url_for('admin.list_classrooms'))

    return render_template('update_classroom.html', form=form)



def update_classroom(classroom_id,classroom_capacity):
    mysql = admin_blp.mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "Update classrooms set classroom_capacity=%s where classroom_id=%s"
    cursor.execute(query,(classroom_capacity,classroom_id))
    conn.commit()
    cursor.close()
    
@admin_blp.route('/generate_msc_timetable')
def generate_msc_timetable():
    return redirect(url_for('timetable.generate_msc_timetable'))

@admin_blp.route('/generate_mca_timetable')
def generate_mca_timetable():
    return redirect(url_for('timetable.generate_mca_timetable'))
