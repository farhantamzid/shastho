# Project Brief: Shastho

## Overview

Shastho is a web-based application designed to enhance public healthcare in Bangladesh by providing a centralized National Electronic Health Record (EHR) and a streamlined online Appointment Scheduling System for public hospitals. The system aims to solve the problems of fragmented patient medical histories and inefficient manual appointment booking processes.

## Core Objectives

1. Establish a centralized Electronic Health Record (EHR) system
2. Create an efficient appointment scheduling system for public hospitals
3. Support various user roles (Patients, Doctors, Hospital Admins, System Admins, Tests/Imaging Admins, Government)
4. Provide secure role-based access to health information
5. Enable health analytics for government oversight

## Technical Approach

- **Backend**: Python Flask framework
- **Frontend**: HTML, CSS with Tailwind CSS (no complex frameworks)
- **Database**: PostgreSQL managed via Supabase
- **Authentication**: Simple database-based authentication
- **Design**: Follow patterns from frontendExamples/ folder

## Implementation Phases

1. **Foundation & Core Patient/Doctor MVP** - Basic user models, authentication, appointment booking
2. **EHR Core & Basic Interactions** - Core EHR structure, prescriptions, test requests
3. **Enhanced Features & Feedback** - Appointment management, feedback system, government portal
4. **Analytics & Advanced Administration** - Government dashboards, outbreak notifications, advanced views

## Key Constraints

- Maintain simplicity in implementation
- Follow design patterns from frontendExamples/
- Support both Bangla and English languages
- Ensure accessibility (WCAG compliance)
- Responsive design for all screen sizes
