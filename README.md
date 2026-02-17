# 💸 Spendly | AI Powered Expense Management System

Spendly is a modern Flask based financial management web application that allows users to securely manage accounts, track expenses, view analytics, and generate reports inside a clean SaaS style dashboard interface.

This project demonstrates backend development, database integration, authentication systems, and basic AI powered financial analysis.

---

## 🚀 Features

🔐 Secure Authentication  
• User signup and login  
• Password hashing using Werkzeug  
• Session management using Flask Login  
• Protected routes  

📊 Dashboard  
• Financial overview  
• Clean responsive navigation  
• Dynamic active navbar  

💳 Accounts Management  
• Add and manage financial accounts  
• User specific data storage  
• SQLite database integration  

📈 AI Analytics  
• Linear Regression using NumPy  
• Z Score anomaly detection  
• Data driven insights  

📑 Reports  
• Structured financial summaries  
• Organized reporting layout  
• Future export ready structure  

---

## 🛠 Tech Stack

Backend  
• Flask  
• Python  

Database  
• SQLite  
• SQLAlchemy ORM  

Authentication  
• Flask Login  
• Werkzeug password hashing  

AI Logic  
• NumPy  

Frontend  
• HTML  
• CSS  
• Bootstrap  
• JavaScript  

Architecture  
• App Factory Pattern  
• Blueprints  

---

## 📂 Project Structure

Spendly/
│
├── __init__.py              # App factory configuration
├── main.py                  # Application entry point
├── auth.py                  # Authentication routes
├── views.py                 # Dashboard, charts, reports routes
├── models.py                # Database models
├── ai_models.py             # AI calculations (Regression, Z-score)
├── add_user_columns.py      # Database migration logic
├── seed_data.py             # Sample data generator
│
├── instance/
│   └── spendly.db           # SQLite database
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── accounts.html
│   ├── charts.html
│   ├── reports.html
│   ├── login.html
│   ├── sign_up.html
│   ├── landingpage.html
│   ├── profile.html
│   └── about.html
│
├── static/
│   ├── img.png
│   └── index.js
│
├── requirements.txt
└── README.md

---

## 🧠 Application Architecture

App Factory  
• Initializes Flask app  
• Configures database  
• Registers Blueprints  
• Sets up Login Manager  

Blueprints  
• auth handles authentication  
• views handles main application logic  

---

## 🗄 Database Models

User  
• id  
• email  
• password hashed  
• first_name  
• relationship with financial records  

Financial Records  
• Linked to user  
• Used for analytics  
• Used in AI calculations  

---

## ▶ How To Run The Project

1 Install dependencies  

pip install -r requirements.txt  

If requirements.txt does not install everything  

pip install flask flask-sqlalchemy flask-login numpy  

2 Run the application  

python main.py  

The application will run at  

http://127.0.0.1:5000  

---

## 🌐 Core Routes

/                Landing Page  
/login           Login  
/sign-up         Register  
/dashboard       Dashboard  
/accounts        Account Management  
/charts          AI Analytics  
/reports         Reports  
/logout          Logout  

---

## 🔒 Security Features

• Password hashing  
• Login required routes  
• User specific database queries  
• Secure session handling  

---

## 📌 Future Improvements

• Monthly analytics dashboard  
• Export to CSV or PDF  
• Advanced AI forecasting  
• Cloud deployment  
• Enhanced UI animations  

---

## 👩‍💻 Author

Shreya Jolapara  
GitHub  
https://github.com/Shreya-J-5  

Flask Development | Backend Systems | AI Integration  

---

## 📄 License

This project is created for educational and portfolio purposes.
