from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange

class AddProfessorForm(FlaskForm):
    professor_id = StringField('Professor ID', validators=[DataRequired(), Length(max=6)])
    name = StringField('Professor Name', validators=[DataRequired(), Length(max=25)])
    submit = SubmitField('Add Professor')

class AddCourseForm(FlaskForm):
    course_number = StringField('Course Number', validators=[DataRequired(), Length(max=5)])
    course_name = StringField('Course Name', validators=[DataRequired(), Length(max=40)])
    max_numb_students = IntegerField('Max Number of Students', validators=[DataRequired(), NumberRange(min=1)])
   # professors = QuerySelectMultipleField('Course Professors', query_factory=professor_choices, get_label='name')
    professors = SelectMultipleField('Course Professors', coerce=int)  # Use int for professor IDs
    submit = SubmitField('Add Course')



class AddLectureForm(FlaskForm):
    time_slots = [
        ('9:30 - 10:30', '9:30 - 10:30'),
        ('10:30 - 11:30', '10:30 - 11:30'),
        ('11:30 - 12:30', '11:30 - 12:30'),
        ('12:30 - 1:30', '12:30 - 1:30'),
        ('2:30 - 3:30', '2:30 - 3:30'),
        ('3:30 - 4:30', '3:30 - 4:30'),
        ('4:30 - 5:30', '4:30 - 5:30'),
    ]
    days_of_week = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    course = SelectField('Course', coerce=int, validators=[DataRequired()])
    classroom = SelectField('Classroom', coerce=int, validators=[DataRequired()])
    time = SelectField('Time Slot', choices=time_slots, validators=[DataRequired()])
    day_of_week = SelectField('Day of the Week', choices=days_of_week, validators=[DataRequired()])
    submit = SubmitField('Schedule Lecture.')

class AddClassroomForm(FlaskForm):
    classroom_name = StringField('Classroom Name', validators = [DataRequired()])
    classroom_capacity = IntegerField('Classroom Capacity', validators = [DataRequired(),NumberRange(min=1)])
    submit = SubmitField(' Add Classroom ')

