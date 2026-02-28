"""
PyTech Arena - Complete Frontend Templates
All HTML templates consolidated into a single file for easy deployment
"""

# Base Template
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --accent-color: #f59e0b;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --dark-text: #1f2937;
            --light-text: #6b7280;
            --border-color: #e5e7eb;
            --background: #f9fafb;
            --radius: 0.5rem;
            --radius-lg: 1rem;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--background);
            color: var(--dark-text);
            line-height: 1.6;
        }
        
        .navbar {
            background: white !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 700;
            color: var(--primary-color) !important;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius);
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background: #1d4ed8;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: var(--secondary-color);
            color: white;
        }
        
        .card {
            background: white;
            border-radius: var(--radius-lg);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: none;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .dashboard-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--dark-text);
            margin-bottom: 0.5rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: var(--radius-lg);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .table {
            background: white;
            border-radius: var(--radius-lg);
            overflow: hidden;
        }
        
        .table th {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 1rem;
        }
        
        .actions {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .profile-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 1.5rem;
            background: var(--background);
            border-radius: var(--radius);
        }
        
        .stat-value {
            display: block;
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }
        
        .stat-label {
            display: block;
            font-size: 0.875rem;
            color: var(--light-text);
            margin-top: 0.5rem;
        }
        
        .job-item {
            background: var(--background);
            padding: 1.5rem;
            border-radius: var(--radius);
            margin-bottom: 1rem;
        }
        
        .badge {
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
        }
        
        .bg-success { background: var(--success-color) !important; }
        .bg-warning { background: var(--warning-color) !important; }
        .bg-danger { background: var(--danger-color) !important; }
        .bg-info { background: var(--primary-color) !important; }
        
        .activity-feed {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .activity-item {
            display: flex;
            align-items: start;
            gap: 1rem;
            padding: 1rem 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            flex-shrink: 0;
        }
        
        .progress {
            height: 20px;
            background: var(--background);
            border-radius: 9999px;
            overflow: hidden;
        }
        
        .progress-bar {
            background: var(--success-color);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: white;
            padding: 2rem;
            border-radius: var(--radius-lg);
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .form-control {
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 0.75rem;
        }
        
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .alert {
            border-radius: var(--radius);
            border: none;
            padding: 1rem;
        }
        
        .alert-success { background: #d1fae5; color: #065f46; }
        .alert-danger { background: #fee2e2; color: #991b1b; }
        .alert-info { background: #dbeafe; color: #1e40af; }
        .alert-warning { background: #fef3c7; color: #92400e; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">
                <i class="fas fa-graduation-cap"></i> PyTech Arena
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('register') }}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="container my-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-light text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0">&copy; 2024 PyTech Arena - JNTU GV Placement Cell. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# Home Page
HOME_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container">
    <div class="row align-items-center min-vh-100">
        <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">Welcome to PyTech Arena</h1>
            <p class="lead mb-4">JNTU GV College of Engineering Placement Cell</p>
            <p class="mb-4">Connect talented students with top companies. Build your career with our comprehensive placement management system.</p>
            <div class="d-flex gap-3">
                <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg">Get Started</a>
                <a href="{{ url_for('register') }}" class="btn btn-outline-primary btn-lg">Register</a>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="text-center">
                <i class="fas fa-graduation-cap display-1 text-primary"></i>
            </div>
        </div>
    </div>
</div>
""")

# Login Page
LOGIN_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Login - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="text-center mb-4">
                <i class="fas fa-user-circle display-4 text-primary"></i>
                <h2 class="mt-3">Login</h2>
                <p class="text-muted">Access your account</p>
            </div>
            <form method="POST">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
            <div class="text-center mt-3">
                <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
            </div>
        </div>
    </div>
</div>
""")

# Register Page
REGISTER_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Register - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
        <div class="card">
            <div class="text-center mb-4">
                <i class="fas fa-user-plus display-4 text-primary"></i>
                <h2 class="mt-3">Register</h2>
                <p class="text-muted">Create your account</p>
            </div>
            <form method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <div class="mb-3">
                    <label for="role" class="form-label">Role</label>
                    <select class="form-control" id="role" name="role">
                        <option value="student">Student</option>
                        <option value="recruiter">Recruiter</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary w-100">Register</button>
            </form>
            <div class="text-center mt-3">
                <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
            </div>
        </div>
    </div>
</div>
""")

# Admin Dashboard
ADMIN_DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Admin Dashboard - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="dashboard-header">
    <h1>Admin/Placement Officer Dashboard</h1>
    <p>Comprehensive placement management system</p>
</div>

<div class="actions">
    <a href="{{ url_for('admin_management') }}" class="btn primary">Access Management</a>
    <a href="{{ url_for('admin_students') }}" class="btn secondary">Manage Students</a>
    <a href="{{ url_for('admin_recruiters') }}" class="btn secondary">Manage Recruiters</a>
    <a href="{{ url_for('admin_analytics') }}" class="btn secondary">View Analytics</a>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <h3>{{ total_students }}</h3>
        <p>Total Students</p>
    </div>
    <div class="stat-card">
        <h3>{{ placed_students }}</h3>
        <p>Placed Students</p>
    </div>
    <div class="stat-card">
        <h3>{{ placement_rate }}%</h3>
        <p>Placement Rate</p>
    </div>
    <div class="stat-card">
        <h3>{{ total_students - placed_students }}</h3>
        <p>Pending Placements</p>
    </div>
</div>

<div class="export-section text-center my-4">
    <a href="{{ url_for('admin_export_report') }}" class="btn primary">
        <i class="fas fa-download"></i> Export Placement Report
    </a>
</div>

{% if dept_stats %}
<div class="card">
    <h2>Department-wise Statistics</h2>
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>Department</th>
                    <th>Total Students</th>
                    <th>Placed Students</th>
                    <th>Placement Rate</th>
                    <th>Average GPA</th>
                </tr>
            </thead>
            <tbody>
                {% for dept, stats in dept_stats.items() %}
                <tr>
                    <td><strong>{{ dept }}</strong></td>
                    <td>{{ stats.count }}</td>
                    <td><span class="badge bg-success">{{ stats.placed }}</span></td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-success" role="progressbar" 
                                 style="width: {{ stats.placement_rate }}%">
                                {{ stats.placement_rate }}%
                            </div>
                        </div>
                    </td>
                    <td><span class="badge bg-info">{{ stats.avg_gpa }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}
""")

# Admin Analytics
ADMIN_ANALYTICS_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Analytics & Reports - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="dashboard-header">
    <h1>Analytics & Reports</h1>
    <p>Comprehensive placement statistics and insights</p>
</div>

<div class="actions">
    <a href="{{ url_for('admin_dashboard') }}" class="btn secondary">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
    </a>
    <a href="{{ url_for('admin_analytics_export') }}" class="btn primary">
        <i class="fas fa-download"></i> Export Analytics
    </a>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <h3>{{ total_students }}</h3>
        <p>Total Students</p>
    </div>
    <div class="stat-card">
        <h3>{{ placed_students }}</h3>
        <p>Placed</p>
    </div>
    <div class="stat-card">
        <h3>{{ not_placed_students }}</h3>
        <p>Not Placed</p>
    </div>
    <div class="stat-card">
        <h3>{{ "%.1f"|format(placement_rate) }}%</h3>
        <p>Placement Rate</p>
    </div>
    <div class="stat-card">
        <h3>{{ total_recruiters }}</h3>
        <p>Total Recruiters</p>
    </div>
    <div class="stat-card">
        <h3>{{ active_recruiters }}</h3>
        <p>Active Recruiters</p>
    </div>
    <div class="stat-card">
        <h3>{{ "%.1f"|format(recruiter_success_rate) }}%</h3>
        <p>Recruiter Success Rate</p>
    </div>
    <div class="stat-card">
        <h3>{{ recent_students }}</h3>
        <p>New (7 days)</p>
    </div>
</div>

<div class="card">
    <h2>Department-wise Statistics</h2>
    <table class="table">
        <thead>
            <tr>
                <th>Department</th>
                <th>Total Students</th>
                <th>Average GPA</th>
            </tr>
        </thead>
        <tbody>
            {% if dept_stats %}
                {% if dept_stats.items() is defined %}
                    {% for dept, stats in dept_stats.items() %}
                    <tr>
                        <td>{{ dept or 'Not Specified' }}</td>
                        <td>{{ stats.count }}</td>
                        <td>{{ "%.2f"|format(stats.avg_gpa) if stats.avg_gpa else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    {% for dept, count, avg_gpa in dept_stats %}
                    <tr>
                        <td>{{ dept or 'Not Specified' }}</td>
                        <td>{{ count }}</td>
                        <td>{{ "%.2f"|format(avg_gpa) if avg_gpa else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                {% endif %}
            {% else %}
            <tr>
                <td colspan="3" class="text-center">No department data available</td>
            </tr>
            {% endif %}
        </tbody>
    </table>
</div>
""")

# Student Dashboard
STUDENT_DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Student Dashboard - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="dashboard-header">
    <h1>Student Dashboard</h1>
    <p>Welcome back, {{ current_user.name }}!</p>
</div>

<div class="actions">
    <a href="{{ url_for('student_edit') }}" class="btn primary">
        <i class="fas fa-user-edit"></i> Edit Profile
    </a>
    <a href="{{ url_for('student_upload') }}" class="btn secondary">
        <i class="fas fa-upload"></i> Upload Documents
    </a>
    <a href="{{ url_for('student_opportunities') }}" class="btn secondary">
        <i class="fas fa-briefcase"></i> View Opportunities
    </a>
    <a href="{{ url_for('student_status') }}" class="btn secondary">
        <i class="fas fa-chart-line"></i> View Status
    </a>
</div>

<div class="card">
    <h2>Your Profile</h2>
    {% if profile %}
    <div class="row">
        <div class="col-md-6">
            <p><strong>Department:</strong> {{ profile.department or 'Not specified' }}</p>
            <p><strong>GPA:</strong> {{ profile.gpa or 'N/A' }}</p>
            <p><strong>Placement Status:</strong> {{ profile.placement_status }}</p>
        </div>
        <div class="col-md-6">
            <p><strong>Skills:</strong> {{ profile.skills or 'Not specified' }}</p>
            <p><strong>Career Preferences:</strong> {{ profile.career_preferences or 'Not specified' }}</p>
        </div>
    </div>
    {% else %}
    <p>You haven't created your profile yet. <a href="{{ url_for('student_edit') }}">Create your profile now</a>.</p>
    {% endif %}
</div>

<div class="card">
    <h2>Recent Activity</h2>
    <div class="activity-feed">
        <div class="activity-item">
            <i class="fas fa-bell activity-icon" style="background: var(--primary-color);"></i>
            <div class="activity-content">
                <p><strong>New Opportunity Available</strong></p>
                <small>Software Engineer position at TechCorp is now open for applications</small>
            </div>
        </div>
        <div class="activity-item">
            <i class="fas fa-info-circle activity-icon" style="background: var(--secondary-color);"></i>
            <div class="activity-content">
                <p><strong>Profile Verification</strong></p>
                <small>Your profile has been verified by the placement officer</small>
            </div>
        </div>
    </div>
</div>
""")

# Student Status
STUDENT_STATUS_TEMPLATE = BASE_TEMPLATE.replace("{% block title %}PyTech Arena - JNTU GV PLACEMENT CELL{% endblock %}", "{% block title %}Placement Status - PyTech Arena{% endblock %}").replace("{% block content %}{% endblock %}", """
<div class="dashboard-header">
    <h1>Placement Status</h1>
    <p>Track your placement journey and application status</p>
</div>

<div class="card">
    <h2>Your Current Status</h2>
    <div class="profile-stats">
        <div class="stat-item">
            <span class="stat-value">{{ profile.placement_status if profile else 'Not Placed' }}</span>
            <span class="stat-label">Placement Status</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{{ profile.gpa if profile else 'N/A' }}</span>
            <span class="stat-label">GPA</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{{ profile.department if profile else 'N/A' }}</span>
            <span class="stat-label">Department</span>
        </div>
    </div>
</div>

<div class="card">
    <h2>Application History</h2>
    {% if opportunities %}
    <div class="job-listings">
        {% for opp in opportunities %}
        <div class="job-item">
            <h3>{{ opp.title }}</h3>
            <p class="job-meta">{{ opp.location }} | {{ opp.type }} | {{ opp.salary }}</p>
            <p><strong>Status:</strong> 
                {% if opp.status == 'Applied' %}
                <span style="color: var(--primary-color); font-weight: 600;">
                    {{ opp.status }}
                </span>
                {% else %}
                <span style="color: var(--success-color); font-weight: 600;">
                    {{ opp.status }}
                </span>
                {% endif %}
            </p>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <p>No applications yet. Browse opportunities and apply!</p>
    {% endif %}
    <a href="{{ url_for('student_opportunities') }}" class="btn primary mt-2">View Opportunities</a>
</div>
""")

# 404 Error Page
ERROR_404_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-md-6 text-center">
        <div class="card">
            <i class="fas fa-exclamation-triangle display-1 text-warning mb-4"></i>
            <h1>404</h1>
            <h2>Page Not Found</h2>
            <p class="text-muted">The page you're looking for doesn't exist.</p>
            <a href="{{ url_for('home') }}" class="btn btn-primary">Go Home</a>
        </div>
    </div>
</div>
""")

# 500 Error Page
ERROR_500_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="row justify-content-center">
    <div class="col-md-6 text-center">
        <div class="card">
            <i class="fas fa-server-error display-1 text-danger mb-4"></i>
            <h1>500</h1>
            <h2>Internal Server Error</h2>
            <p class="text-muted">Something went wrong on our end. We're working to fix it.</p>
            <a href="{{ url_for('home') }}" class="btn btn-primary">Go Home</a>
        </div>
    </div>
</div>
""")

# Template Registry
TEMPLATES = {
    'base.html': BASE_TEMPLATE,
    'index.html': HOME_TEMPLATE,
    'login.html': LOGIN_TEMPLATE,
    'register.html': REGISTER_TEMPLATE,
    'admin_dashboard.html': ADMIN_DASHBOARD_TEMPLATE,
    'admin_analytics.html': ADMIN_ANALYTICS_TEMPLATE,
    'student_dashboard.html': STUDENT_DASHBOARD_TEMPLATE,
    'student_status.html': STUDENT_STATUS_TEMPLATE,
    '404.html': ERROR_404_TEMPLATE,
    '500.html': ERROR_500_TEMPLATE,
}

def get_template(template_name):
    """Get template by name"""
    return TEMPLATES.get(template_name, BASE_TEMPLATE)

# Export all templates for use in the backend
__all__ = ['get_template', 'TEMPLATES']
