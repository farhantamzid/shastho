"""
Regulatory body routes for the Shastho Flask application.
-------------------------------------------------------
This file defines all routes related to the regulatory dashboard, outbreak, and disease management.
Each route is registered as part of the 'regulatory_body_bp' blueprint in app/__init__.py.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import login_required, role_required
from app.models.database import UserRole
from app.utils.db import Database
from app.services.regulatory_service import get_dashboard_data

# Create Blueprint for regulatory body routes
regulatory_body_bp = Blueprint('regulatory_body', __name__, url_prefix='/regulatory')
db = Database()

# Regulatory Body Dashboard route
@regulatory_body_bp.route('/dashboard')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def dashboard():
    """
    Regulatory Body Dashboard - Entry point for government regulatory users
    Shows aggregated health data for monitoring disease outbreaks
    """
    # Get the user ID from session (unused now but kept for consistency)
    user_id = session.get('user_id')

    # Fetch data from MySQL
    data = get_dashboard_data()

    user_name = session.get('user_name', 'Regulatory Official')

    return render_template(
        'regulatory_body/dashboard.html',
        user_name=user_name,
        **data
    )

# Disease Details route
@regulatory_body_bp.route('/disease/<disease_name>')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def disease_details(disease_name):
    """
    Disease Details - Show detailed information about a specific disease
    """
    # Dummy data for diseases
    disease_data = {
        'Dengue Fever': {
            'name': 'Dengue Fever',
            'cases': 4582,
            'trend': 'increasing',
            'risk_level': 'high',
            'description': 'Dengue fever is a mosquito-borne tropical disease caused by the dengue virus. Symptoms typically begin 3-14 days after infection and may include high fever, headache, vomiting, muscle and joint pain, and a characteristic skin rash.',
            'transmission': 'Transmitted primarily by female Aedes mosquitoes, particularly A. aegypti.',
            'symptoms': ['High fever (40°C/104°F)', 'Headache', 'Muscle and joint pain', 'Rash', 'Vomiting', 'Pain behind the eyes'],
            'prevention': ['Control mosquito populations', 'Use mosquito repellents', 'Wear long-sleeved clothing', 'Use mosquito nets', 'Eliminate standing water'],
            'treatments': ['No specific antiviral treatment', 'Supportive care with fluid replacement', 'Pain relievers (avoiding aspirin)', 'Rest', 'Monitoring for complications'],
            'affected_regions': [
                {'name': 'Dhaka Division', 'cases': 1872, 'trend': 'Increasing'},
                {'name': 'Chittagong Division', 'cases': 987, 'trend': 'Increasing'},
                {'name': 'Khulna Division', 'cases': 423, 'trend': 'Stable'},
                {'name': 'Sylhet Division', 'cases': 621, 'trend': 'Increasing'},
                {'name': 'Barisal Division', 'cases': 389, 'trend': 'Decreasing'}
            ],
            'monthly_trend': [125, 156, 243, 375, 456, 678, 892],
            'age_distribution': {
                'Under 10': 18,
                '11-20': 24,
                '21-30': 32,
                '31-40': 12,
                '41-50': 8,
                'Over 50': 6
            }
        },
        'Malaria': {
            'name': 'Malaria',
            'cases': 876,
            'trend': 'increasing',
            'risk_level': 'high',
            'description': 'Malaria is a life-threatening disease caused by parasites transmitted to people through the bites of infected female Anopheles mosquitoes.',
            'transmission': 'Transmitted through the bites of infected female Anopheles mosquitoes.',
            'symptoms': ['Fever', 'Chills', 'Headache', 'Nausea', 'Vomiting', 'Muscle pain', 'Fatigue'],
            'prevention': ['Use insecticide-treated mosquito nets', 'Indoor residual spraying', 'Preventive medications', 'Reduce mosquito habitats', 'Wear protective clothing'],
            'treatments': ['Antimalarial medications', 'Artemisinin-based combination therapies (ACTs)', 'Supportive care', 'Management of complications'],
            'affected_regions': [
                {'name': 'Chittagong Division', 'cases': 423, 'trend': 'Increasing'},
                {'name': 'Sylhet Division', 'cases': 287, 'trend': 'Stable'},
                {'name': 'Rangpur Division', 'cases': 112, 'trend': 'Decreasing'},
                {'name': 'Mymensingh Division', 'cases': 54, 'trend': 'Stable'}
            ],
            'monthly_trend': [223, 198, 210, 227, 252, 286, 312],
            'age_distribution': {
                'Under 10': 22,
                '11-20': 18,
                '21-30': 20,
                '31-40': 16,
                '41-50': 14,
                'Over 50': 10
            }
        },
        'COVID-19': {
            'name': 'COVID-19',
            'cases': 542,
            'trend': 'increasing',
            'risk_level': 'medium',
            'description': 'COVID-19 is an infectious disease caused by the SARS-CoV-2 virus, which can cause respiratory illness with symptoms such as cough, fever, and difficulty breathing.',
            'transmission': 'Primarily transmitted through respiratory droplets when infected people breathe, talk, cough, or sneeze.',
            'symptoms': ['Fever', 'Cough', 'Shortness of breath', 'Fatigue', 'Loss of taste or smell', 'Sore throat', 'Headache'],
            'prevention': ['Vaccination', 'Mask-wearing', 'Social distancing', 'Hand hygiene', 'Adequate ventilation'],
            'treatments': ['Antiviral medications', 'Supportive care', 'Oxygen therapy', 'Monoclonal antibody treatment', 'Rest and hydration'],
            'affected_regions': [
                {'name': 'Dhaka Division', 'cases': 287, 'trend': 'Increasing'},
                {'name': 'Chittagong Division', 'cases': 124, 'trend': 'Stable'},
                {'name': 'Rajshahi Division', 'cases': 69, 'trend': 'Increasing'},
                {'name': 'Khulna Division', 'cases': 62, 'trend': 'Stable'}
            ],
            'monthly_trend': [556, 423, 378, 402, 435, 489, 542],
            'age_distribution': {
                'Under 10': 5,
                '11-20': 8,
                '21-30': 15,
                '31-40': 23,
                '41-50': 26,
                'Over 50': 23
            }
        }
    }

    # Default to Dengue Fever if disease not found
    if disease_name not in disease_data:
        disease_name = 'Dengue Fever'

    disease = disease_data[disease_name]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

    user_name = session.get('user_name', 'Regulatory Official')

    return render_template('regulatory_body/disease_details.html',
                          user_name=user_name,
                          disease=disease,
                          months=months)

# Region Details route
@regulatory_body_bp.route('/region/<region_name>')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def region_details(region_name):
    """
    Region Details - Show detailed health information about a specific region
    """
    # Dummy data for region details
    region_data = {
        'Dhaka Division': {
            'name': 'Dhaka Division',
            'total_cases': 4125,
            'active_outbreaks': 3,
            'population': '36 million',
            'population_affected': '0.82%',
            'hospital_capacity': '76%',
            'hospitals': 42,
            'healthcare_workers': 1245,
            'primary_diseases': [
                {'name': 'Dengue Fever', 'cases': 1872, 'trend': 'Increasing'},
                {'name': 'COVID-19', 'cases': 287, 'trend': 'Increasing'},
                {'name': 'Tuberculosis', 'cases': 823, 'trend': 'Stable'},
                {'name': 'Influenza', 'cases': 643, 'trend': 'Increasing'},
                {'name': 'Typhoid', 'cases': 500, 'trend': 'Decreasing'}
            ],
            'monthly_trend': [1234, 1356, 1543, 2375, 2856, 3278, 4125],
            'districts': [
                {'name': 'Dhaka', 'cases': 2356, 'hospital_capacity': '85%'},
                {'name': 'Gazipur', 'cases': 675, 'hospital_capacity': '72%'},
                {'name': 'Narayanganj', 'cases': 543, 'hospital_capacity': '68%'},
                {'name': 'Tangail', 'cases': 321, 'hospital_capacity': '59%'},
                {'name': 'Manikganj', 'cases': 230, 'hospital_capacity': '52%'}
            ]
        },
        'Chittagong Division': {
            'name': 'Chittagong Division',
            'total_cases': 2784,
            'active_outbreaks': 2,
            'population': '29 million',
            'population_affected': '0.54%',
            'hospital_capacity': '65%',
            'hospitals': 35,
            'healthcare_workers': 985,
            'primary_diseases': [
                {'name': 'Malaria', 'cases': 423, 'trend': 'Increasing'},
                {'name': 'Typhoid', 'cases': 678, 'trend': 'Stable'},
                {'name': 'Dengue Fever', 'cases': 987, 'trend': 'Increasing'},
                {'name': 'Cholera', 'cases': 396, 'trend': 'Decreasing'},
                {'name': 'COVID-19', 'cases': 300, 'trend': 'Stable'}
            ],
            'monthly_trend': [987, 1124, 1342, 1687, 2043, 2456, 2784],
            'districts': [
                {'name': 'Chittagong', 'cases': 1245, 'hospital_capacity': '75%'},
                {'name': 'Cox\'s Bazar', 'cases': 567, 'hospital_capacity': '72%'},
                {'name': 'Rangamati', 'cases': 432, 'hospital_capacity': '58%'},
                {'name': 'Bandarban', 'cases': 287, 'hospital_capacity': '49%'},
                {'name': 'Khagrachari', 'cases': 253, 'hospital_capacity': '48%'}
            ]
        }
    }

    # Default to Dhaka Division if region not found
    if region_name not in region_data:
        region_name = 'Dhaka Division'

    region = region_data[region_name]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

    user_name = session.get('user_name', 'Regulatory Official')

    return render_template('regulatory_body/region_details.html',
                          user_name=user_name,
                          region=region,
                          months=months)

# Outbreak Details route
@regulatory_body_bp.route('/outbreak/<int:outbreak_id>')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def outbreak_details(outbreak_id):
    """
    Outbreak Details - Show detailed information about a specific disease outbreak
    """
    # Dummy data for outbreaks
    outbreaks = [
        {
            'id': 1,
            'disease': 'Dengue Fever',
            'region': 'Dhaka Division',
            'cases': 278,
            'deaths': 12,
            'status': 'Active',
            'trend': 'Increasing',
            'start_date': '2023-07-01',
            'severity': 'High',
            'description': 'Major dengue outbreak affecting multiple districts in Dhaka Division, with highest concentration in urban areas.',
            'response_measures': [
                'Increased mosquito control operations',
                'Public awareness campaigns',
                'Additional hospital beds allocated',
                'Mobile medical teams deployed',
                'Vector surveillance intensified'
            ],
            'affected_areas': [
                {'district': 'Dhaka City', 'cases': 142, 'trend': 'Increasing'},
                {'district': 'Gazipur', 'cases': 57, 'trend': 'Increasing'},
                {'district': 'Narayanganj', 'cases': 43, 'trend': 'Stable'},
                {'district': 'Savar', 'cases': 36, 'trend': 'Increasing'}
            ],
            'daily_cases': [8, 12, 15, 18, 22, 24, 27, 32, 30, 35, 37, 40, 43, 45],
            'age_distribution': {
                'Under 10': 15,
                '11-20': 28,
                '21-30': 32,
                '31-40': 14,
                '41-50': 7,
                'Over 50': 4
            }
        },
        {
            'id': 2,
            'disease': 'Cholera',
            'region': 'Barisal Division',
            'cases': 156,
            'deaths': 8,
            'status': 'Active',
            'trend': 'Stable',
            'start_date': '2023-06-15',
            'severity': 'Medium',
            'description': 'Waterborne outbreak following recent flooding in coastal areas of Barisal Division.',
            'response_measures': [
                'Clean water distribution',
                'ORS distribution centers established',
                'Water purification tablets distributed',
                'Sanitation improvement campaigns',
                'Temporary treatment centers'
            ],
            'affected_areas': [
                {'district': 'Barisal City', 'cases': 68, 'trend': 'Stable'},
                {'district': 'Bhola', 'cases': 42, 'trend': 'Decreasing'},
                {'district': 'Patuakhali', 'cases': 35, 'trend': 'Stable'},
                {'district': 'Pirojpur', 'cases': 11, 'trend': 'Decreasing'}
            ],
            'daily_cases': [12, 15, 18, 16, 14, 12, 10, 9, 8, 11, 9, 10, 7, 5],
            'age_distribution': {
                'Under 10': 23,
                '11-20': 18,
                '21-30': 15,
                '31-40': 16,
                '41-50': 14,
                'Over 50': 14
            }
        }
    ]

    # Default to first outbreak if ID not found
    outbreak = next((o for o in outbreaks if o['id'] == outbreak_id), outbreaks[0])
    days = [f'Day {i+1}' for i in range(len(outbreak['daily_cases']))]

    user_name = session.get('user_name', 'Regulatory Official')

    return render_template('regulatory_body/outbreak_details.html',
                          user_name=user_name,
                          outbreak=outbreak,
                          days=days)

# Regulatory Body Profile route
@regulatory_body_bp.route('/profile')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def profile():
    """
    Regulatory Body Profile - View and edit profile information
    """
    # Get the user ID from session
    user_id = session.get('user_id')

    # Dummy profile data
    profile = {
        'name': 'John Doe',
        'email': 'john.doe@health.gov',
        'agency': 'Department of Health Services',
        'role': 'Senior Health Inspector',
        'jurisdiction': 'Central District',
        'badge_number': 'R-7845',
        'contact': '+1 (555) 123-4567'
    }

    return render_template('regulatory_body/profile.html', profile=profile)