from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, HiddenField, BooleanField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional
from app.models.ehr import AllergySeverity

class DiagnosisForm(FlaskForm):
    """Form for adding or editing a diagnosis"""
    visit_id = HiddenField('Visit ID')
    diagnosis_code = StringField('Diagnosis Code', validators=[DataRequired(), Length(min=2, max=20)])
    diagnosis_description = TextAreaField('Diagnosis Description', validators=[DataRequired(), Length(min=3, max=500)])
    diagnosed_at = DateField('Diagnosis Date', validators=[DataRequired()])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])

class MedicationForm(FlaskForm):
    """Form for adding or editing a medication"""
    visit_id = HiddenField('Visit ID')
    medication_name = StringField('Medication Name', validators=[DataRequired(), Length(min=2, max=100)])
    dosage = StringField('Dosage', validators=[DataRequired(), Length(min=1, max=50)])
    frequency = StringField('Frequency', validators=[DataRequired(), Length(min=1, max=100)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    instructions = TextAreaField('Instructions/Notes', validators=[Optional(), Length(max=500)])

class PrescriptionForm(FlaskForm):
    """Form for creating a prescription"""
    visit_id = HiddenField('Visit ID')
    medication_name = StringField('Medication Name', validators=[DataRequired(), Length(min=2, max=100)])
    dosage = StringField('Dosage', validators=[DataRequired(), Length(min=1, max=50)])
    frequency = StringField('Frequency', validators=[DataRequired(), Length(min=1, max=100)])
    duration = StringField('Duration', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = StringField('Quantity', validators=[DataRequired(), Length(min=1, max=20)])
    refills = StringField('Refills', validators=[Optional(), Length(max=10)])
    instructions = TextAreaField('Instructions', validators=[DataRequired(), Length(min=3, max=500)])
    dispense_as_written = BooleanField('Dispense As Written')

class AllergyForm(FlaskForm):
    """Form for adding or editing an allergy"""
    visit_id = HiddenField('Visit ID')
    allergen = StringField('Allergen', validators=[DataRequired(), Length(min=2, max=100)])
    reaction = TextAreaField('Reaction', validators=[DataRequired(), Length(min=3, max=500)])
    severity = SelectField('Severity', choices=[(s.name, s.value) for s in AllergySeverity], validators=[DataRequired()])
    onset_date = DateField('Onset Date', validators=[Optional()])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])

class ImmunizationForm(FlaskForm):
    """Form for adding or editing an immunization"""
    visit_id = HiddenField('Visit ID')
    vaccine = StringField('Vaccine Name', validators=[DataRequired(), Length(min=2, max=100)])
    date_administered = DateField('Date Administered', validators=[DataRequired()])
    administered_by = StringField('Administered By', validators=[Optional(), Length(max=100)])
    lot_number = StringField('Lot Number', validators=[Optional(), Length(max=50)])
    site = StringField('Administration Site', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

class VitalSignsForm(FlaskForm):
    """Form for adding or editing vital signs"""
    visit_id = HiddenField('Visit ID')
    temperature = StringField('Temperature (°F)', validators=[Optional(), Length(max=10)])
    pulse = StringField('Pulse (bpm)', validators=[Optional(), Length(max=10)])
    blood_pressure = StringField('Blood Pressure', validators=[Optional(), Length(max=20)])
    respiratory_rate = StringField('Respiratory Rate (bpm)', validators=[Optional(), Length(max=10)])
    oxygen_saturation = StringField('Oxygen Saturation (%)', validators=[Optional(), Length(max=10)])
    height = StringField('Height', validators=[Optional(), Length(max=10)])
    weight = StringField('Weight', validators=[Optional(), Length(max=10)])
    bmi = StringField('BMI', validators=[Optional(), Length(max=10)])
    recorded_at = DateField('Date Recorded', validators=[DataRequired()])

class ProviderNoteForm(FlaskForm):
    """Form for adding or editing provider notes"""
    visit_id = HiddenField('Visit ID')
    note_type = SelectField('Note Type', choices=[
        ('progress', 'Progress Note'),
        ('soap', 'SOAP Note'),
        ('procedure', 'Procedure Note'),
        ('consultation', 'Consultation'),
        ('discharge', 'Discharge Summary'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    note_text = TextAreaField('Note', validators=[DataRequired(), Length(min=10, max=10000)])
    note_date = DateField('Date', validators=[DataRequired()])
    is_private = BooleanField('Private Note (visible only to providers)')

    # SOAP Note specific fields (shown conditionally in UI when note_type is 'soap')
    subjective = TextAreaField('Subjective', validators=[Optional(), Length(max=5000)])
    objective = TextAreaField('Objective', validators=[Optional(), Length(max=5000)])
    assessment = TextAreaField('Assessment', validators=[Optional(), Length(max=5000)])
    plan = TextAreaField('Plan', validators=[Optional(), Length(max=5000)])

class TestResultForm(FlaskForm):
    """Form for adding test results"""
    visit_id = HiddenField('Visit ID')
    test_name = StringField('Test Name', validators=[DataRequired(), Length(min=2, max=100)])
    test_date = DateField('Test Date', validators=[DataRequired()])
    test_description = TextAreaField('Test Description', validators=[Optional(), Length(max=500)])
    test_result = TextAreaField('Result', validators=[DataRequired(), Length(min=1, max=1000)])
    test_units = StringField('Units', validators=[Optional(), Length(max=20)])
    reference_range = StringField('Reference Range', validators=[Optional(), Length(max=100)])
    is_abnormal = BooleanField('Abnormal Result')
    result_interpretation = TextAreaField('Interpretation', validators=[Optional(), Length(max=1000)])
    test_file = FileField('Attach Result Document')

class ProcedureForm(FlaskForm):
    """Form for adding or editing a procedure"""
    visit_id = HiddenField('Visit ID')
    procedure_code = StringField('Procedure Code', validators=[DataRequired(), Length(min=2, max=20)])
    procedure_description = TextAreaField('Procedure Description', validators=[DataRequired(), Length(min=3, max=500)])
    performed_at = DateField('Procedure Date', validators=[DataRequired()])
    performed_by = StringField('Performed By', validators=[Optional(), Length(max=100)])
    procedure_notes = TextAreaField('Procedure Notes', validators=[Optional(), Length(max=5000)])
    attachments = MultipleFileField('Attachments')