import logging

from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from models import get_all_courses, get_all_professors, get_all_lectures, get_all_classrooms, generate_valid_timetables,add_lecture
import pdfkit
import os


logging.basicConfig(level=logging.DEBUG)

timetable_blp = Blueprint('timetable', __name__, static_folder='static', template_folder='templates/timetable')


@timetable_blp.route('/timetable/lectures',methods = ['GET','POST'])
def list_lectures():
    lectures = get_all_lectures()
    logging.debug(f'Listing lectures: {lectures}')

    return render_template('lectures.html', lectures=lectures)



@timetable_blp.route('/delete_lecture/<int:lecture_id>', methods=['GET','POST'])
def delete_lecture(lecture_id):
    try:
        logging.debug(f'Deleting lecture with ID: {lecture_id}')

        # Perform deletion from database (implement as per your database schema)
        # Example: You might have a delete function in models.py
        # add appropriate code here to delete the lecture

        delete_lecture_by_id(lecture_id)  # Example function to delete lecture by ID
        logging.debug(f'Lecture with ID: {lecture_id} successfully deleted')


        flash('Lecture deleted successfully!', 'success')
        return redirect(url_for('timetable.list_lectures'))  # Redirect to lectures list after deletion
        #return render_template('lectures.html')

    except Exception as e:
        logging.error(f'Error deleting lecture: {str(e)}')
        flash(f'Error deleting lecture: {str(e)}', 'danger')
        return redirect(url_for('timetable.list_lectures'))
        #return render_template('lectures.html')

def delete_lecture_by_id(lecture_id):
    from app import mysql
    #mysql = admin_blp.mysql

    logging.debug(f'Inside delete_lecture_by_id with ID: {lecture_id}')

    conn = mysql.connection
    cursor = conn.cursor()
    query = "Delete from lectures where lecture_id= %s"
    cursor.execute(query,(lecture_id,))
    conn.commit()

    logging.debug(f'Lecture with ID: {lecture_id} deleted')

    cursor.close()


@timetable_blp.route('/generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    try:
        logging.debug('Entered generate_timetable route')

        # Generate timetable combinations
        timetable, timeslots, days_of_week = generate_valid_timetables()
        logging.debug(f'Timetable: {timetable}')
        logging.debug(f'Timeslots: {timeslots}')
        logging.debug(f'Days of Week: {days_of_week}')



        # Render the generated timetable to HTML
        rendered = render_template('GenerateTimeTable.html', timetable=timetable, timeslots=timeslots, days_of_week=days_of_week)
        logging.debug(f'Rendered HTML: {rendered}')

        # Generate PDF from the rendered HTML
        pdf_path = 'generated_timetable.pdf'
        pdfkit.from_string(rendered, pdf_path)

        flash('Timetable generated successfully!', 'success')
        return redirect(url_for('timetable.download_timetable'))

    except Exception as e:
        logging.error(f'Error generating timetable: {str(e)}')
        flash(f'Error generating timetable: {str(e)}', 'danger')
        return redirect(url_for('timetable.generate_timetable'))




@timetable_blp.route('/download_timetable')
def download_timetable():
    path = 'generated_timetable.pdf'
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash('Timetable not found. Please generate the timetable first.', 'danger')
        return redirect(url_for('timetable.generate_timetable'))
