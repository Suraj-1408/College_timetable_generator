from flask import Blueprint, flash, redirect, render_template,url_for, send_file
from fpdf import FPDF
from collections import defaultdict
import random, logging, os
from models import get_all_msc_courses, get_all_mca_courses

timetable_blp = Blueprint('timetable', __name__, static_folder='static', template_folder='templates/timetable')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIMESLOTS = ['9:00am - 11:00am', '11:00am - 1:00pm', '2:00pm - 4:00pm', '4:00pm - 6:00pm']

def fetch_courses(program):
    if program == 'MSC':
        return get_all_msc_courses()
    elif program == 'MCA':
        return get_all_mca_courses()
    else:
        return None

def generate_timetables(courses, combinations=5):
    def check_valid_schedule(schedule):
        for day in schedule:
            used_times = set()
            for timeslot in schedule[day]:
                if timeslot in used_times:
                    return False
                used_times.add(timeslot)
        return True

    all_timetables = []

    for _ in range(combinations):
        timetable = {day: {timeslot: '' for timeslot in TIMESLOTS} for day in DAYS}

        for course in courses:
            lectures_remaining = course['no_of_lectures']
            while lectures_remaining > 0:
                day = random.choice(DAYS)
                timeslot = random.choice(TIMESLOTS)

                if timetable[day][timeslot] == '':
                    timetable[day][timeslot] = f"{course['course_name']}"
                    lectures_remaining -= 1

        if check_valid_schedule(timetable):
            all_timetables.append(timetable)

    return all_timetables

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'University Timetable', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def generate_pdf(timetables, filename='timetable.pdf', program=''):
    logger.debug("Generating PDF")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    cell_height = 12  
    cell_width_day = 28.5  
    cell_width_course = 28.5  

    for index, timetable in enumerate(timetables):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"{program} Timetable combination {index + 1}", ln=True, align='C')

        # Timetable Structure
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=" ", ln=True)
        pdf.cell(cell_width_day, cell_height, txt="Timeslot/Day", border=1, align='C')
        
        # Header row for days
        for day in DAYS:
            pdf.cell(cell_width_course, cell_height, txt=day, border=1, align='C')
        pdf.ln()

        # Timetable Cells
        for timeslot in TIMESLOTS:
            max_height = cell_height
            for day in DAYS:
                cell_text = timetable[day][timeslot] if timeslot in timetable[day] else ""
                lines = pdf.multi_cell(cell_width_course, cell_height / 2, txt=cell_text, border=1, align='C', split_only=True)
                max_height = max(max_height, len(lines) * (cell_height / 2))

            # Draw the timeslot cell with the determined maximum height
            pdf.cell(cell_width_day, max_height, txt=timeslot, border=1)
            for day in DAYS:
                cell_text = timetable[day][timeslot] if timeslot in timetable[day] else ""
                pdf.cell(cell_width_course, max_height, txt=cell_text, border=1, align='C')

            pdf.ln(max_height)  # Move to the next row

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf.output(filename)
    logger.debug(f"PDF generated: {filename}")
    return filename


def create_timetables_for_program(program):
    logger.debug(f"Fetching courses for program: {program}")
    courses = fetch_courses(program)

    if not courses:
        logger.error("No courses found for the program")
        return None

    logger.debug(f"Generating timetables for {len(courses)} courses")
    timetables = generate_timetables(courses)
    filename = f'{program}_timetable.pdf'
    filepath = os.path.join(timetable_blp.static_folder, filename)

    generate_pdf(timetables, filepath, program)
    return filepath

@timetable_blp.route('/generate_msc_timetable', methods=['GET', 'POST'])
def generate_msc_timetable():
    try:
        logger.debug("Generating MSC timetable")
        filepath = create_timetables_for_program('MSC')

        if filepath:
            flash(f'MSc timetable generated successfully','success')
            return redirect(url_for('timetable.view_msc_timetable',filename=os.path.basename(filepath)))
        else:
            flash('No courses found for MSc', 'danger')

    except Exception as e:
        logger.error(f'Error while generating MSc timetables: {e}')
        flash(f'Error while generating MSc timetables: {e}', 'danger')
    #return redirect(url_for('admin.list_msc_courses'))
    return redirect(url_for('timetable.view_msc_timetable',filename=os.path.basename(filepath)))

@timetable_blp.route('/generate_mca_timetable', methods=['GET', 'POST'])
def generate_mca_timetable():
    try:
        logger.debug("Generating MCA timetable")
        filepath = create_timetables_for_program('MCA')

        if filepath:
            flash(f'MCA timetable generated successfully. <a href="{url_for("timetable.download_file", filename=os.path.basename(filepath))}">Download PDF</a>', 'success')
        else:
            flash('No courses found for MCA', 'danger')

    except Exception as e:
        logger.error(f'Error while generating MCA timetables: {e}')
        flash(f'Error while generating MCA timetables: {e}', 'danger')
    #return redirect(url_for('admin.list_mca_courses'))
    return redirect(url_for('timetable.view_mca_timetable',filename=os.path.basename(filepath)))


@timetable_blp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(timetable_blp.static_folder, filename)
    return send_file(filepath, as_attachment=True)


@timetable_blp.route('/view_msc_timetable/<filename>',methods=['GET'])
def view_msc_timetable(filename):
    filepath = os.path.join(timetable_blp.static_folder,filename)
    return render_template('view_msc_timetable.html',pdf_path=url_for('timetable.static',filename=filename))

@timetable_blp.route('/view_mca_timetable/<filename>',methods=['GET'])
def view_mca_timetable(filename):
    filepath = os.path.join(timetable_blp.static_folder,filename)
    return render_template('view_mca_timetable.html',pdf_path=url_for('timetable.static',filename=filename))