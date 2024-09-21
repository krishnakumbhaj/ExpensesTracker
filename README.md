Expense Tracker Terminal Application
This is a terminal-based expense tracker application built using Python, FastAPI, and uAgents. The application allows users to track their expenses by adding, viewing, and generating expense reports directly from the terminal. All expense data is stored in a local file (expenses_db.json) for easy retrieval and persistence.

Features
Add Expenses: Record expenses with a description, amount, and category.
View Total Expenses: View the total expenses logged by the current user.
Generate Report: Generate a detailed report of expenses categorized by type.
User Authentication: Users can log in, and their expenses are tracked individually.
Data Persistence: Expenses are saved locally in a JSON file.
Terminal Interface: The app provides a simple, interactive terminal interface using the rich library.
Requirements
Make sure you have the following installed before running the application:

Python 3.x
FastAPI
uAgents
rich
You can install the dependencies using:

bash
Copy code
pip install fastapi uagents rich
Project Structure
bash
Copy code
.
├── agent.py           # Main Python script containing the Expense Tracker logic
├── expenses_db.json   # JSON file where expenses are stored (auto-generated)
├── requirements.txt   # Dependencies for the project
└── README.md          # This README file
agent.py
This is the main script that handles the following tasks:

User authentication
Expense logging
Total expense calculation
Report generation
expenses_db.json
This file stores all user expenses in JSON format. It is created automatically when expenses are logged.

Usage
Clone the repository:
bash
Copy code
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
Install dependencies:
bash
Copy code
pip install -r requirements.txt
Run the application:
bash
Copy code
python agent.py
Follow the terminal prompts:
You will be prompted to log in, add expenses, and generate reports.
Menu Example
bash
Copy code
Expense Tracker Menu for Krishna:
[1] Add Expense
[2] View Total Expenses
[3] Generate Report
[4] Logout
[5] Exit
Choose an option (1-5): 1
Enter expense description: Rent
Enter expense amount: 3000
Enter expense category: housing
File Storage
Expenses are stored in expenses_db.json. If the file is empty or corrupted, the program will reset the expenses and start fresh. Make sure the file remains in JSON format for data integrity.

Contributing
Feel free to fork this project, create pull requests, or submit issues. Any contributions are welcome!
