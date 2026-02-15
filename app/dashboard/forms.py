from flask_wtf import FlaskForm
from wtforms import (
    DateTimeLocalField, TextAreaField, SubmitField,
    StringField, DecimalField, BooleanField
)
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional


class AdjustmentForm(FlaskForm):
    """Manual time adjustment form."""
    clock_in = DateTimeLocalField('Clock In', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    clock_out = DateTimeLocalField('Clock Out', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    note = TextAreaField('Adjustment Note', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Save Adjustment')


class AddEmployeeForm(FlaskForm):
    """Form to add a new employee."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    pin = StringField('4-Digit PIN', validators=[DataRequired(), Length(min=4, max=4)])
    hourly_rate = DecimalField('Hourly Rate ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField('Add Employee')


class EditEmployeeForm(FlaskForm):
    """Form to edit an existing employee."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    pin = StringField('New PIN (leave blank to keep current)', validators=[Optional(), Length(min=4, max=4)])
    hourly_rate = DecimalField('Hourly Rate ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')
