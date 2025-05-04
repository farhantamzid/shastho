# shastho

## Hospital Admin Role and Approval Workflow

### Overview

Shastho implements a multi-tier administration hierarchy to ensure proper management of healthcare facilities:

1. **System Administrators** - Top-level administrators who manage the entire system
2. **Hospital Administrators** - Manage individual hospitals and create requests for additional admin roles
3. **Test/Imaging Administrators** - Specialized administrators responsible for test and imaging departments

### Approval Workflow

1. **Hospital Admin Registration**:

   - Users can register as Hospital Administrators through the registration form
   - Registration puts the account in inactive status
   - System Administrators review and approve Hospital Admin applications

2. **Test/Imaging Admin Creation**:
   - Approved Hospital Admins can create requests for Test/Imaging Administrator roles
   - Each request includes applicant details, qualifications, and department information
   - Hospital Admins can approve or reject these requests
   - When a request is approved, the applicant can register with their approved email address

### Hospital Admin Features

1. **Dashboard**:

   - Overview of hospital statistics
   - Quick access to pending admin requests
   - Navigation to all hospital management features

2. **Profile Management**:

   - Hospital Admins can view and update their profile information
   - Edit personal details like full name, contact number, and address
   - View associated hospital information

3. **Admin Request Management**:
   - Create Test/Imaging Admin requests for hospital departments
   - View all requests with advanced filtering and search capabilities
   - Filter by status (pending, approved, rejected) and department
   - Search requests by name, email, or other criteria
   - Sort requests by various fields (name, date, department, status)
   - View detailed statistics about admin requests
   - Approve or reject pending requests with appropriate workflow

### Features

- Hospital Admin dashboard with statistics and request management
- Detailed view of Test/Imaging Admin applications
- Approval/rejection functionality with status tracking
- Filtering of admin requests by status (pending/approved/rejected)

### User Roles

- **HOSPITAL_ADMIN**: Hospital administrators with permissions to manage their hospital and create admin requests
- **TEST_ADMIN**: Test and imaging department administrators
- **ADMIN**: System administrators with global permissions

### Status Tracking

All admin requests include tracking information:

- Creation date and time
- Last update timestamp
- Current status (pending, approved, rejected)
