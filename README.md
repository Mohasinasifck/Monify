# 💰 Monify - Personal Expense Tracker

A beautiful, modern Flask web application for tracking personal expenses with advanced features and admin panel.


[![GitHub Stars](https://img.shields.io/github/stars/Mohasinasifck/Monify?style=for-the-badge)](https://github.com/Mohasinasifck/Monify/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Mohasinasifck/Monify?style=for-the-badge)](https://github.com/Mohasinasifck/Monify/network/members)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![Flask Version](https://img.shields.io/badge/Flask-2.3+-green.svg?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)

## ✨ Features

### 🎯 Core Features
- **🔐 User Authentication** - Secure registration and login system with session management
- **💸 Expense Management** - Complete CRUD operations for expense tracking
- **🏷️ Category System** - Custom expense categories with colors and icons
- **📊 Dashboard** - Beautiful overview with statistics and visual data representation
- **📤 CSV Export** - Export your financial data anytime for external analysis
- **🔍 Search & Filter** - Advanced filtering and search capabilities
- **📱 Mobile Responsive** - Optimized for all devices and screen sizes
- **🔄 Recurring Expenses** - Set up and manage automatic recurring expenses

### 🛡️ Admin Panel
- **📊 Admin Dashboard** - Comprehensive overview of all users and system metrics
- **👥 User Management** - View, manage, and monitor user accounts
- **📋 Expense Monitoring** - Monitor all expenses across the platform
- **📈 Analytics & Reports** - Detailed insights and financial reports
- **🏷️ Category Management** - Full control over expense categories
- **🔒 Role-based Access** - Secure admin authentication and permissions

### 🎨 Design Features
- **✨ Modern Glass-morphism UI** - Beautiful frosted glass effects with gradients
- **🌈 Smooth Animations** - Professional transitions and micro-interactions
- **🎯 Intuitive UX** - Clean, user-friendly interface design
- **🎪 Consistent Styling** - Professional design language throughout


## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.8+** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Anaconda/Miniconda** (Recommended) - [Download Anaconda](https://anaconda.com/products/distribution)

### ⚡ Installation

- **📥 Clone the repository**
```
git clone https://github.com/Mohasinasifck/Monify.git
cd Monify
```

- **🐍 Create and activate conda environment**
```
conda env create -f environment.yml
conda activate monify
```

- **🗄️ Initialize the database**
```
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized!')"
```

- **🚀 Run the application**
```
python app.py
```

### 🌐 Access the Application

1. **Main Application**: Open `http://localhost:5000`
2. **Admin Panel**: Visit `http://localhost:5000/admin/login`

**Default Admin Credentials:**
- Email: `admin@monify.com`
- Password: `admin123` ⚠️ **Change immediately after first login!**

## 📖 Usage Guide

### 👤 For Regular Users

1. **📝 Register** - Create your personal account with email verification
2. **🔑 Login** - Secure access to your personal dashboard
3. **💸 Add Expenses** - Record expenses with detailed categorization
4. **🏷️ Manage Categories** - Create and customize expense categories
5. **📊 View Analytics** - Analyze spending patterns with visual charts
6. **📤 Export Data** - Download your financial data as CSV
7. **🔄 Set Recurring** - Automate regular expense entries

### 👨‍💼 For Administrators

1. **🔐 Admin Login** - Secure access via `/admin/login`
2. **📊 Monitor Dashboard** - Overview of platform metrics and activity
3. **👥 Manage Users** - View user accounts and activity logs
4. **💰 Track Expenses** - Monitor all platform expenses and trends
5. **📈 Generate Reports** - Create detailed analytical reports
6. **🏷️ Control Categories** - Manage available expense categories
7. **⚙️ System Settings** - Configure platform-wide settings

## 🛠️ Technology Stack

<table>
<tr>
<td><strong>Backend</strong></td>
<td>
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlite&logoColor=white" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
</td>
</tr>
<tr>
<td><strong>Frontend</strong></td>
<td>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5">
<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript">
<img src="https://img.shields.io/badge/Bootstrap-563D7C?style=flat-square&logo=bootstrap&logoColor=white" alt="Bootstrap">
</td>
</tr>
<tr>
<td><strong>Database</strong></td>
<td>
<img src="https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
</td>
</tr>
<tr>
<td><strong>Authentication</strong></td>
<td>
<img src="https://img.shields.io/badge/Flask--Login-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask-Login">
</td>
</tr>
</table>

## 📁 Project Structure
```
Monify/
├── 📄 app.py # Main Flask application
├── 📄 requirements.txt # Python dependencies
├── 📄 environment.yml # Conda environment configuration
├── 📄 README.md # This documentation
├── 📄 .gitignore # Git ignore rules
├── 📄 Procfile # Heroku deployment configuration
├── 📄 runtime.txt # Python version specification
├── 📄 LICENSE # MIT License
├── 🗃️ instance/ # Database and instance-specific files
│ └── Monify.db # SQLite database (auto-generated)
├── 🎨 templates/ # Jinja2 HTML templates
│ ├── base.html # Base template with common elements
│ ├── home.html # Landing page
│ ├── login.html # User login page
│ ├── register.html # User registration page
│ ├── dashboard.html # User dashboard
│ ├── expenses.html # Expense management interface
│ ├── add_expense.html # Add new expense form
│ ├── edit_expense.html # Edit expense form
│ ├── categories.html # Category management
│ ├── admin_login.html # Admin login page
│ ├── admin_base.html # Admin base template
│ ├── admin_dashboard.html # Admin dashboard
│ ├── admin_users.html # Admin user management
│ ├── admin_expenses.html # Admin expense oversight
│ └── 404.html # Error page
```


### 🖥️ Render.com Deployment

1. Connect your GitHub repository to Render.com
2. Set **Build Command**: `pip install -r requirements.txt`
3. Set **Start Command**: `python app.py`
4. Add environment variables in Render dashboard
5. Deploy automatically!


## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
1. Check existing issues first
2. Create detailed bug reports with steps to reproduce
3. Include screenshots if applicable

### ✨ Feature Requests
1. Search existing feature requests
2. Create detailed proposals with use cases
3. Consider implementation complexity

### 💻 Pull Requests
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### 📋 Development Guidelines
- Follow **PEP 8** Python style guide
- Add **comments** for complex logic
- Update **tests** for new features
- Update **documentation** as needed
- Test on multiple Python versions

## 📝 API Documentation

### 🔗 Main Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Landing page | No |
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/dashboard` | GET | User dashboard | Yes |
| `/expenses` | GET | View expenses | Yes |
| `/add_expense` | GET, POST | Add new expense | Yes |
| `/edit_expense/<id>` | GET, POST | Edit expense | Yes |
| `/delete_expense/<id>` | POST | Delete expense | Yes |
| `/export_csv` | GET | Export expenses as CSV | Yes |
| `/admin/login` | GET, POST | Admin login | No |
| `/admin/dashboard` | GET | Admin dashboard | Admin |
| `/admin/users` | GET | Manage users | Admin |
| `/admin/expenses` | GET | View all expenses | Admin |

## 🔮 Roadmap & Future Features

### 🎯 Version 2.0
- [ ] 🌙 Dark theme support
- [ ] 📱 Progressive Web App (PWA) capabilities
- [ ] 📊 Advanced charts with Chart.js integration
- [ ] 💰 Budget planning and goal setting
- [ ] 💱 Multi-currency support with live exchange rates

### 🎯 Version 3.0
- [ ] 🔗 RESTful API for third-party integrations
- [ ] 📸 Receipt scanning with OCR technology
- [ ] ⚡ Real-time notifications and alerts
- [ ] 📈 Investment tracking and portfolio management
- [ ] 🤖 AI-powered expense categorization
- [ ] 🏦 Bank account integration

### 🎯 Long-term Goals
- [ ] 📱 Mobile app (React Native/Flutter)
- [ ] 🧠 Machine learning for spending predictions
- [ ] 🔗 Integration with popular financial services
- [ ] 🌐 Multi-language support
- [ ] ☁️ Cloud backup and synchronization

## 📊 Project Statistics

![GitHub repo size](https://img.shields.io/github/repo-size/Mohasinasifck/Monify?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/Mohasinasifck/Monify?style=for-the-badge)
![GitHub top language](https://img.shields.io/github/languages/top/Mohasinasifck/Monify?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/Mohasinasifck/Monify?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Mohasinasifck/Monify?style=for-the-badge)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.



**Made with ❤️ by [Mohasin Asif](https://github.com/Mohasinasifck)**

**🎓 IHUB School of Learning - Mini Project 2025**

⭐ **Star this repository if you find it helpful!**

[![GitHub Stars](https://img.shields.io/github/stars/Mohasinasifck/Monify?style=social)](https://github.com/Mohasinasifck/Monify/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Mohasinasifck/Monify?style=social)](https://github.com/Mohasinasifck/Monify/network/members)
[![GitHub Watchers](https://img.shields.io/github/watchers/Mohasinasifck/Monify?style=social)](https://github.com/Mohasinasifck/Monify/watchers)

---

### 🏆 Project Highlights

🎯 **Complete Expense Management System** | 🔐 **Secure User Authentication** | 👨‍💼 **Advanced Admin Panel**
📊 **Beautiful Data Visualization** | 📱 **Mobile Responsive Design** | 🚀 **Production Ready**

**[⭐ Star](https://github.com/Mohasinasifck/Monify) • [🐛 Report Bug](https://github.com/Mohasinasifck/Monify/issues) • [💡 Request Feature](https://github.com/Mohasinasifck/Monify/discussions)**

</div>


