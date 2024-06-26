from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange

class AddProfessorForm(FlaskForm):
    #professor_id = StringField('Professor ID', validators=[DataRequired(), Length(max=6)])
    name = StringField('Professor Name', validators=[DataRequired(), Length(max=25)])
    submit = SubmitField('Add Professor')

class AddCourseForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    professor_name = SelectField('Professor', coerce=str, validators=[DataRequired()])
    total_credits = IntegerField('Total Credits', validators=[DataRequired()])
    no_of_lectures = IntegerField('No. of Lectures per Week', validators=[DataRequired()])
    submit = SubmitField('Add Course')

class AddMCACourseForm(FlaskForm):
    course_name = StringField('course Name',validators=[DataRequired()])
    professor_name = SelectField('Professor',coerce=str, validators=[DataRequired()])
    total_credits = IntegerField('Total Credits',validators=[DataRequired()])
    no_of_lectures = IntegerField('No of Lectures per Week', validators=[DataRequired()])
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
    classroom_id = StringField('Classroom ID') 
    classroom_capacity = IntegerField('Classroom Capacity', validators = [DataRequired(),NumberRange(min=1)])
    submit = SubmitField('Add Classroom')

class UpdateClassroomForm(FlaskForm):
    classroom_capacity = IntegerField('Classroom Capacity',validators = [DataRequired()])
    submit = SubmitField('Update Classroom')
