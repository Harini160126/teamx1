# PyTech Arena - Placement Support System

PyTech Arena is a comprehensive web-based platform designed to streamline university placement processes. It connects students, placement officers, and recruiters through a unified, intuitive interface.

## Features

### For Students:
- Create and manage detailed placement profiles
- Upload resumes and profile photos
- Track placement status in real-time
- View personalized job recommendations

### For Placement Officers:
- Verify and manage student data
- Generate department-wise and skill-based reports
- Monitor placement statistics
- Update placement status for students

### For Recruiters:
- Browse structured student profiles
- Filter candidates by GPA, skills, and department
- Access to qualified candidate pool

## Technology Stack

- **Backend**: Python, Flask Framework
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Additional Libraries**: Werkzeug (security), Jinja2 (templating)

## Installation & Setup

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```
3. Initialize the database:
   ```bash
   flask init-db
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Visit `http://127.0.0.1:5000` in your browser

## Default Credentials

After initialization, a default admin account is created:
- **Email**: admin@example.com
- **Password**: admin123

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS prevention through template autoescaping

## Project Structure

```
pytecharena/
├── app.py                 # Main Flask application
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── student_dashboard.html  # Student dashboard
│   ├── student_profile.html    # Student profile editor
│   ├── admin_dashboard.html    # Admin dashboard
│   ├── admin_students.html     # Admin student management
│   └── recruiter_dashboard.html # Recruiter dashboard
├── static/               # Static assets
│   ├── css/              # Style sheets
│   │   └── style.css     # Main stylesheet
│   ├── js/               # JavaScript files
│   │   └── main.js       # Main JavaScript
│   └── images/           # Image assets
├── uploads/              # File uploads (resumes, photos)
├── dataset_preprocessing_report.md  # Data processing documentation
├── system_architecture.txt          # System architecture diagram
├── Presentation.md       # Project presentation
└── README.md            # This file
```

## Database Schema

### User Table:
- id (Primary Key)
- name
- email (Unique)
- password_hash
- role (student/admin/recruiter)
- created_at

### StudentProfile Table:
- id (Primary Key)
- user_id (Foreign Key)
- department
- gpa
- skills
- internships
- projects
- certifications
- career_preferences
- resume_filename
- photo_filename
- placement_status

## Usage Instructions

1. **Register as a Student**: Navigate to the registration page and create a student account
2. **Complete Your Profile**: Fill in your academic details, skills, and experiences
3. **Track Your Status**: Monitor your placement status as it gets updated
4. **Admin Functions**: Use admin credentials to manage students and update placement statuses
5. **Recruiter Functions**: Recruiters can search and filter students based on various criteria

## Customization

The application can be easily customized by:
- Modifying the CSS in `static/css/style.css`
- Updating templates in the `templates/` directory
- Adding new routes and functionality in `app.py`

## Production Deployment

For production use:
1. Change the SECRET_KEY in app.py
2. Use a production-grade database like PostgreSQL
3. Deploy behind a production WSGI server (Gunicorn, uWSGI)
4. Set `debug=False` in the app.run() call

## Credits

PyTech Arena was developed as a comprehensive placement management solution demonstrating full-stack Python web development capabilities.