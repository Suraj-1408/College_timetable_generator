from flask import Flask,Blueprint,render_template,request,redirect,url_for,session,current_app
import MySQLdb.cursors
import re

admin_blp = Blueprint('admin',__name__,static_folder='static',template_folder='templates/admin')



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

