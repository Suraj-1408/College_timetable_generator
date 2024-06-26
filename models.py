import logging
import MySQLdb  
import pdb

''' Utility function to add a professor
def add_professor(professor_id, name):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    query = "INSERT INTO professors (professor_id, name) VALUES (%s, %s)"
    cursor.execute(query, (professor_id, name))
    conn.commit()
    cursor.close()
'''

def  gen_professor_id():
    from app import mysql

    try:
        conn = mysql.connection
        cursor = conn.cursor()
        
        query = "SELECT MAX(CAST(SUBSTRING(professor_id, 6) AS UNSIGNED)) AS max_id FROM professors"
        cursor.execute(query)
        result = cursor.fetchone()

        print(f"Result from the query:{result}")

        next_no = 101
        if result and result.get('max_id') is not None:
            next_no = result['max_id']+ 1
       
        #return f"PUCSD{next_no:03d}"
        professor_id = f"PUCSD{next_no}"
        print(f"Generated professor ID:{professor_id}")
        return professor_id

    except Exception as e:
        print(f"Error in gen_professor_id():{e}")
        return None

    finally:
        #conn.commit()
        cursor.close()
        


def add_professor(professor_id,name):
    from app import mysql
    conn = mysql.connection
    cursor =conn.cursor()


    try:        
        query = "INSERT INTO professors (professor_id, name) VALUES (%s, %s)"
        cursor.execute(query,(professor_id,name))
        conn.commit()
        flash('Professor Added Successfully','success')
        #return professor_id

        cursor.execute("SELECT professor_id FROM professors WHERE professor_id = %s",(professor_id,))
        result = cursor.fetchone()
        return result['professor_id']

    except Exception as e:
        print(f"Error in add_professor:{e}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        #conn.close()

# Utility function to get all professors
def get_all_professors():
    
        from app import mysql   
        conn = mysql.connection
        cursor = conn.cursor()

        query = "SELECT * FROM professors"
        cursor.execute(query)
        professors = cursor.fetchall()
        
        
        conn.commit()
        cursor.close()






#utility function for generarting course_id for msc & mca courses
def gen_course_id(program_name,prefix,start_number):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    try:
        query = f"select max(cast(substring(course_id,length(%s)+1)as unsigned)) as max_id from {program_name}"
        cursor.execute(query,(prefix,))
        result = cursor.fetchone()
        max_id = result['max_id'] if result['max_id'] is not None else start_number - 1
        next_id = max_id +1
        return f"{prefix}{next_id}"

    except Exception as e:
        print(f'Error in gen_course_id():{e}')
        return None

    finally:
        
        cursor.close()
        


def gen_msc_course_id():
    return gen_course_id('msc_courses','CS-',551)

def gen_mca_course_id():
    return gen_course_id('mca_courses','CA-',201)



# Utility function to add a course
def add_course(course_number, course_name, max_numb_students):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO courses (course_number, course_name, max_numb_students) VALUES (%s, %s, %s)"
    cursor.execute(query, (course_number, course_name, max_numb_students))
    conn.commit()
    cursor.close()


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





#Utility function to generate classroom id by the system.
def gen_classroom_id():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    try:
        query = "Select max(cast(substring(classroom_id, 2) as unsigned)) as max_id from classrooms"
        cursor.execute(query)
        result = cursor.fetchone()
        max_id = result['max_id'] if result['max_id'] is not None  else 0
        next_id = max_id + 1
        return f"C{next_id}"

    except Exception as e:
        print(f'Error in gen_classroom_id():{e}')
        return None

    finally:
        conn.commit()
        cursor.close()
        




def add_classroom(classroom_capacity):
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    try:
        classroom_id = gen_classroom_id()

        if classroom_id:        
            query = "INSERT INTO classrooms (classroom_id,classroom_capacity) VALUES (%s,%s)"
            cursor.execute(query, (classroom_id,classroom_capacity))
            conn.commit()
            flash('Classroom added Successfully','success')
        
        else:
            flash('Error while generating classroom Id','danger')

    except Exception as e:
        flash(f'Error adding Classroom:{e}','danger')

    finally:
        cursor.close()

def get_all_classrooms():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT classroom_id,classroom_capacity FROM classrooms"
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


def get_all_msc_courses():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    query = "Select * from msc_courses"
    cursor.execute(query)
    msc_courses = cursor.fetchall()
    cursor.close()
    return msc_courses


def get_all_mca_courses():
    from app import mysql
    conn = mysql.connection
    cursor = conn.cursor()

    query = "Select * from mca_courses"
    cursor.execute(query)
    mca_courses = cursor.fetchall()
    cursor.close()
    return mca_courses