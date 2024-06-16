#from app import mysql
#from flask import current_app
#from TimeTable_Schedule import mysql 

import logging
import MySQLdb  # Import MySQLdb module here

# Utility function to add a professor
def add_professor(professor_id, name):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    query = "INSERT INTO professors (professor_id, name) VALUES (%s, %s)"
    cursor.execute(query, (professor_id, name))
    conn.commit()
    cursor.close()


# Utility function to get all professors
def get_all_professors():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT * FROM professors"
    cursor.execute(query)
    professors = cursor.fetchall()
    cursor.close()
    return professors

# Utility function to add a course
def add_course(course_number, course_name, max_numb_students):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO courses (course_number, course_name, max_numb_students) VALUES (%s, %s, %s)"
    cursor.execute(query, (course_number, course_name, max_numb_students))
    conn.commit()
    cursor.close()

# Utility function to get all courses
def get_all_courses():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT * FROM courses"
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()
    return courses



# Utility function to associate professors with a course
def add_professors_to_course(course_id, professor_ids):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    query = "INSERT INTO course_professor (course_id, professor_id) VALUES (%s, %s)"
    for professor_id in professor_ids:
        cursor.execute(query, (course_id, professor_id))
    conn.commit()
    cursor.close()



#Utility Function to add add Lecture.
def add_lecture(course_id,classroom_id, time_slot, day_of_week):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO lectures (course_id,classroom_id, time_slot, day_of_week) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (course_id,classroom_id, time_slot, day_of_week))
    conn.commit()
    cursor.close()



def get_all_lectures():
    from app import mysql
    logging.debug('Fetching all lectures')

    conn = mysql.connection
    cursor = conn.cursor()

    query = """
    SELECT l.lecture_id, c.course_name,cl.classroom_name, l.time_slot, l.day_of_week
    FROM lectures l
    JOIN courses c ON l.course_id = c.course_id
    JOIN classrooms cl ON l.classroom_id = cl.classroom_id 
    """
    cursor.execute(query)
    lectures = cursor.fetchall()

    cursor.close()
    logging.debug(f'Fetched lectures: {lectures}')

    return lectures



def add_classroom(classroom_name):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO classrooms (classroom_name) VALUES (%s)"
    cursor.execute(query, (classroom_name,))
    conn.commit()
    cursor.close()

def get_all_classrooms():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT classroom_id, classroom_name,classroom_capacity FROM classrooms"
    cursor.execute(query)
    classrooms = cursor.fetchall()
    cursor.close()
    return classrooms


# Function to create tables
def create_tables():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    
    create_query = '''
     CREATE TABLE IF NOT EXISTS professors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        uid VARCHAR(6) NOT NULL,
        name VARCHAR(25) NOT NULL
    )
    '''     
    
    cursor.execute(create_query)
    mysql.connection.commit()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_number VARCHAR(5) NOT NULL,
        course_name VARCHAR(40) NOT NULL,
        max_numb_students INT NOT NULL
    )
    """)
    conn.commit()
    cursor.close()


'''

def is_conflict(existing_entries, new_entry):
    for entry in existing_entries:
        if entry['time_slot'] == new_entry['time_slot'] and entry['day_of_week'] == new_entry['day_of_week']:
            if entry['course']['course_id'] == new_entry['course']['course_id']:
                return True
    return False
'''


def generate_valid_timetables():
    logging.debug('Entered generate_valid_timetables function')

    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    # Fetch existing lectures
    lectures = get_all_lectures()

    logging.debug(f'Lectures: {lectures}')  # Log the data to check the structure

    timeslots = ['9:30 - 10:30', '10:30 - 11:30', '11:30 - 12:30', '12:30 - 1:30', '2:30 - 3:30', '3:30 - 4:30', '4:30 - 5:30']
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    timetable = {day: {timeslot: None for timeslot in timeslots} for day in days_of_week}

    for lecture in lectures:
        course_name = lecture['course_name']
        time_slot = lecture['time_slot']
        day_of_week = lecture['day_of_week']
        if timetable[day_of_week][time_slot] is None:
            timetable[day_of_week][time_slot] = course_name

    cursor.close()
    logging.debug(f'Generated timetable: {timetable}')
    return timetable, timeslots, days_of_week
