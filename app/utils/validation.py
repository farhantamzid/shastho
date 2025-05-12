"""
Validation utility functions for the Shastho Flask application.
-------------------------------------------------------------
This file contains helper functions for validating user input and data throughout the app.
Used in forms, routes, and services to ensure data integrity.
"""
from typing import List, Dict, Any, Optional, Union, Callable, TypeVar
from datetime import datetime, date
import re
from uuid import UUID
from flask import flash

T = TypeVar('T')

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")

class ValidationResult:
    """Result of a validation operation"""
    def __init__(self, success: bool = True, errors: Optional[List[ValidationError]] = None):
        self.success = success
        self.errors = errors or []

    def add_error(self, field: str, message: str, value: Any = None):
        """Add an error to the validation result"""
        self.errors.append(ValidationError(field, message, value))
        self.success = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'success': self.success,
            'errors': [
                {
                    'field': err.field,
                    'message': err.message,
                    'value': str(err.value) if err.value is not None else None
                }
                for err in self.errors
            ]
        }

    def get_error_messages(self) -> List[str]:
        """Get list of error messages"""
        return [f"{err.field}: {err.message}" for err in self.errors]

    def flash_errors(self):
        """Flash all error messages for use in templates"""
        for error in self.errors:
            flash(f"{error.field}: {error.message}", 'error')

class Validator:
    """Base validator class"""
    def __init__(self, field_name: str):
        self.field_name = field_name

    def validate(self, value: Any) -> ValidationResult:
        """Validate a value"""
        raise NotImplementedError("Subclasses must implement validate()")

class RequiredValidator(Validator):
    """Validator for required fields"""
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult()
        if value is None or (isinstance(value, str) and value.strip() == ''):
            result.add_error(self.field_name, "This field is required", value)
        return result

class StringLengthValidator(Validator):
    """Validator for string length"""
    def __init__(self, field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None):
        super().__init__(field_name)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Optional[str]) -> ValidationResult:
        result = ValidationResult()

        if value is None:
            return result

        if not isinstance(value, str):
            result.add_error(self.field_name, "Must be a string", value)
            return result

        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(
                self.field_name,
                f"Must be at least {self.min_length} characters",
                value
            )

        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(
                self.field_name,
                f"Must not exceed {self.max_length} characters",
                value
            )

        return result

class EmailValidator(Validator):
    """Validator for email format"""
    def validate(self, value: Optional[str]) -> ValidationResult:
        result = ValidationResult()

        if value is None or value.strip() == '':
            return result

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            result.add_error(self.field_name, "Invalid email format", value)

        return result

class DateValidator(Validator):
    """Validator for date values"""
    def __init__(self, field_name: str, min_date: Optional[date] = None, max_date: Optional[date] = None):
        super().__init__(field_name)
        self.min_date = min_date
        self.max_date = max_date

    def validate(self, value: Optional[Union[date, datetime, str]]) -> ValidationResult:
        result = ValidationResult()

        if value is None:
            return result

        # Convert to date if it's a datetime or string
        try:
            if isinstance(value, datetime):
                value = value.date()
            elif isinstance(value, str):
                value = datetime.strptime(value, "%Y-%m-%d").date()
            elif not isinstance(value, date):
                result.add_error(self.field_name, "Invalid date format", value)
                return result
        except ValueError:
            result.add_error(self.field_name, "Invalid date format", value)
            return result

        if self.min_date is not None and value < self.min_date:
            result.add_error(
                self.field_name,
                f"Date must be on or after {self.min_date.isoformat()}",
                value
            )

        if self.max_date is not None and value > self.max_date:
            result.add_error(
                self.field_name,
                f"Date must be on or before {self.max_date.isoformat()}",
                value
            )

        return result

class NumericValidator(Validator):
    """Validator for numeric values"""
    def __init__(
        self,
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        is_integer: bool = False
    ):
        super().__init__(field_name)
        self.min_value = min_value
        self.max_value = max_value
        self.is_integer = is_integer

    def validate(self, value: Optional[Union[int, float, str]]) -> ValidationResult:
        result = ValidationResult()

        if value is None or (isinstance(value, str) and value.strip() == ''):
            return result

        # Convert string to number if needed
        if isinstance(value, str):
            try:
                if self.is_integer:
                    value = int(value)
                else:
                    value = float(value)
            except ValueError:
                result.add_error(
                    self.field_name,
                    "Must be a valid number",
                    value
                )
                return result

        if not isinstance(value, (int, float)):
            result.add_error(
                self.field_name,
                "Must be a number",
                value
            )
            return result

        if self.is_integer and not isinstance(value, int):
            result.add_error(
                self.field_name,
                "Must be an integer",
                value
            )
            return result

        if self.min_value is not None and value < self.min_value:
            result.add_error(
                self.field_name,
                f"Must be greater than or equal to {self.min_value}",
                value
            )

        if self.max_value is not None and value > self.max_value:
            result.add_error(
                self.field_name,
                f"Must be less than or equal to {self.max_value}",
                value
            )

        return result

class PatternValidator(Validator):
    """Validator for regex patterns"""
    def __init__(self, field_name: str, pattern: str, message: str = "Invalid format"):
        super().__init__(field_name)
        self.pattern = pattern
        self.message = message
        self.compiled_pattern = re.compile(pattern)

    def validate(self, value: Optional[str]) -> ValidationResult:
        result = ValidationResult()

        if value is None or value.strip() == '':
            return result

        if not isinstance(value, str):
            result.add_error(self.field_name, "Must be a string", value)
            return result

        if not self.compiled_pattern.match(value):
            result.add_error(self.field_name, self.message, value)

        return result

class CustomValidator(Validator):
    """Validator for custom validation functions"""
    def __init__(self, field_name: str, validate_func: Callable[[Any], Union[bool, str]], message: str = None):
        super().__init__(field_name)
        self.validate_func = validate_func
        self.default_message = message or "Invalid value"

    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult()

        validation_result = self.validate_func(value)

        if validation_result is False:
            result.add_error(self.field_name, self.default_message, value)
        elif isinstance(validation_result, str):
            result.add_error(self.field_name, validation_result, value)

        return result

class ModelValidator:
    """Validator for models"""
    def __init__(self):
        self.validators: Dict[str, List[Validator]] = {}

    def add_validator(self, field_name: str, validator: Validator):
        """Add a validator for a field"""
        if field_name not in self.validators:
            self.validators[field_name] = []

        self.validators[field_name].append(validator)
        return self

    def add_rule(self, field_name: str, *validators: Validator):
        """Add multiple validators for a field"""
        for validator in validators:
            self.add_validator(field_name, validator)
        return self

    def required(self, field_name: str):
        """Add a required validator for a field"""
        return self.add_validator(field_name, RequiredValidator(field_name))

    def string_length(self, field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """Add a string length validator for a field"""
        return self.add_validator(field_name, StringLengthValidator(field_name, min_length, max_length))

    def email(self, field_name: str):
        """Add an email validator for a field"""
        return self.add_validator(field_name, EmailValidator(field_name))

    def date(self, field_name: str, min_date: Optional[date] = None, max_date: Optional[date] = None):
        """Add a date validator for a field"""
        return self.add_validator(field_name, DateValidator(field_name, min_date, max_date))

    def numeric(
        self,
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        is_integer: bool = False
    ):
        """Add a numeric validator for a field"""
        return self.add_validator(
            field_name,
            NumericValidator(field_name, min_value, max_value, is_integer)
        )

    def pattern(self, field_name: str, pattern: str, message: str = "Invalid format"):
        """Add a pattern validator for a field"""
        return self.add_validator(field_name, PatternValidator(field_name, pattern, message))

    def custom(self, field_name: str, validate_func: Callable[[Any], Union[bool, str]], message: str = None):
        """Add a custom validator for a field"""
        return self.add_validator(field_name, CustomValidator(field_name, validate_func, message))

    def validate_field(self, field_name: str, value: Any) -> ValidationResult:
        """Validate a single field"""
        result = ValidationResult()

        if field_name not in self.validators:
            return result

        for validator in self.validators[field_name]:
            validator_result = validator.validate(value)
            for error in validator_result.errors:
                result.add_error(error.field, error.message, error.value)

        return result

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate all fields in the data"""
        result = ValidationResult()

        for field_name, validators in self.validators.items():
            value = data.get(field_name)

            for validator in validators:
                validator_result = validator.validate(value)
                for error in validator_result.errors:
                    result.add_error(error.field, error.message, error.value)

        return result

# Common validation rule sets
def patient_validation_rules() -> ModelValidator:
    """Get validation rules for patients"""
    today = date.today()

    return ModelValidator() \
        .required('full_name') \
        .string_length('full_name', min_length=2, max_length=100) \
        .required('date_of_birth') \
        .date('date_of_birth', max_date=today) \
        .required('gender') \
        .required('contact_number') \
        .pattern('contact_number', r'^\+?[0-9]{10,15}$', "Phone number must be 10-15 digits") \
        .required('address') \
        .string_length('address', min_length=5, max_length=255) \
        .required('emergency_contact_name') \
        .string_length('emergency_contact_name', min_length=2, max_length=100) \
        .required('emergency_contact_number') \
        .pattern('emergency_contact_number', r'^\+?[0-9]{10,15}$', "Phone number must be 10-15 digits")

def doctor_validation_rules() -> ModelValidator:
    """Get validation rules for doctors"""
    return ModelValidator() \
        .required('full_name') \
        .string_length('full_name', min_length=2, max_length=100) \
        .required('specialization') \
        .string_length('specialization', min_length=2, max_length=100) \
        .required('credentials') \
        .string_length('credentials', min_length=2, max_length=500) \
        .required('hospital_id') \
        .required('department_id') \
        .required('contact_number') \
        .pattern('contact_number', r'^\+?[0-9]{10,15}$', "Phone number must be 10-15 digits")

def diagnosis_validation_rules() -> ModelValidator:
    """Get validation rules for diagnoses"""
    return ModelValidator() \
        .required('diagnosis_description') \
        .string_length('diagnosis_description', min_length=2, max_length=500) \
        .required('diagnosis_code') \
        .string_length('diagnosis_code', min_length=2, max_length=20) \
        .required('visit_id')

def medication_validation_rules() -> ModelValidator:
    """Get validation rules for medications"""
    return ModelValidator() \
        .required('medication_name') \
        .string_length('medication_name', min_length=2, max_length=100) \
        .required('dosage') \
        .string_length('dosage', min_length=1, max_length=50) \
        .required('frequency') \
        .string_length('frequency', min_length=1, max_length=100) \
        .required('start_date') \
        .required('visit_id')

def provider_note_validation_rules() -> ModelValidator:
    """Get validation rules for provider notes"""
    return ModelValidator() \
        .required('note_text') \
        .string_length('note_text', min_length=2, max_length=10000) \
        .required('visit_id')