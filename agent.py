from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import threading
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from passlib.context import CryptContext
from uagents import Agent, Context
import json
import os

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# File to store user data
USER_DATA_FILE = "users_db.json"
EXPENSE_DATA_FILE = "expenses_db.json"

# Load users from file if it exists
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save users to file
def save_users():
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users_db, file)

# Load expenses from file if it exists
# Load expenses from file if it exists
# Load expenses from file if it exists
def load_expenses():
    if os.path.exists("expenses_db.json"):
        try:
            with open("expenses_db.json", "r") as file:
                data = json.load(file)
                # Convert dictionaries back to Expense objects
                return {username: [Expense(**expense) for expense in expenses] for username, expenses in data.items()}
        except json.JSONDecodeError:
            # Handle case where JSON is empty or corrupted
            print("Error loading expenses. File might be empty or corrupted. Starting with empty expenses.")
            return {}
    else:
        return {}



# Save expenses to file
# Save expenses to file
def save_expenses():
    # Convert the list of Expense objects into dictionaries before saving
    expenses_serializable = {username: [expense.dict() for expense in expenses] for username, expenses in agent.expenses.items()}
    with open("expenses_db.json", "w") as file:
        json.dump(expenses_serializable, file)


# Load users and expenses into in-memory databases on startup
users_db = load_users()

# Models
class Expense(BaseModel):
    id: int
    description: str
    amount: float
    category: str

class ExpenseReport(BaseModel):
    total_expenses: float
    expenses_by_category: Dict[str, float]

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: str

# Expense Tracker Agent
class ExpenseTrackerAgent(Agent):
    def __init__(self):
        super().__init__(name="Expense Tracker Agent", port=8000)
        self.expenses: Dict[str, List[Expense]] = load_expenses()  # Load expenses from file
        self.next_id: Dict[str, int] = {user: len(expenses) + 1 for user, expenses in self.expenses.items()}  # Track ID per user
        self.sessions: Dict[str, bool] = {}  # Track user login status

    async def add_expense(self, ctx: Context, username: str, description: str, amount: float, category: str) -> Expense:
     if username not in self.expenses:
        self.expenses[username] = []
        self.next_id[username] = 1
     expense = Expense(id=self.next_id[username], description=description, amount=amount, category=category)
     self.expenses[username].append(expense)
     self.next_id[username] += 1
     save_expenses()  # Save expenses to file after each addition
     return expense


    async def get_total_expenses(self, ctx: Context, username: str) -> float:
        if username in self.expenses:
            return sum(expense.amount for expense in self.expenses[username])
        return 0

    async def get_expenses_by_category(self, ctx: Context, username: str) -> Dict[str, float]:
        expenses_by_category = {}
        if username in self.expenses:
            for expense in self.expenses[username]:
                if expense.category not in expenses_by_category:
                    expenses_by_category[expense.category] = 0
                expenses_by_category[expense.category] += expense.amount
        return expenses_by_category

    async def generate_report(self, ctx: Context, username: str) -> ExpenseReport:
        total = await self.get_total_expenses(ctx, username)
        by_category = await self.get_expenses_by_category(ctx, username)
        return ExpenseReport(total_expenses=total, expenses_by_category=by_category)

    async def login(self, ctx: Context, username: str, password: str) -> bool:
        """Handles login via the agent."""
        if username in users_db and verify_password(password, users_db[username]['password']):
            if not self.sessions.get(username, False):
                self.sessions[username] = True
                return True
        return False

    async def logout(self, ctx: Context, username: str) -> bool:
        """Logs out the user via the agent."""
        if self.sessions.get(username, False):
            self.sessions[username] = False
            return True
        return False

    def is_logged_in(self, username: str) -> bool:
        """Check if the user is already logged in."""
        return self.sessions.get(username, False)

# FastAPI setup
app = FastAPI()
agent = ExpenseTrackerAgent()

# Terminal Interface
console = Console()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def display_expense_report(report):
    table = Table(title="Expense Report")
    table.add_column("Category", justify="center", style="cyan")
    table.add_column("Total Amount", justify="center", style="magenta")

    for category, amount in report.expenses_by_category.items():
        table.add_row(category, f"${amount:.2f}")
    
    console.print(table)
    console.print(f"\nTotal Expenses: ${report.total_expenses:.2f}")

async def terminal_interface():
    current_user = None

    while True:
        if not current_user:
            console.print("\n[bold cyan]Authentication:[/bold cyan]")
            console.print("[1] Register")
            console.print("[2] Login")
            console.print("[3] Exit")

            auth_choice = Prompt.ask("Choose an option (1-3)", choices=["1", "2", "3"])

            if auth_choice == "1":
                username = Prompt.ask("Enter username")
                if username in users_db:
                    console.print(f"[red]Username '{username}' already exists. Please try again.[/red]")
                    continue
                password = Prompt.ask("Enter password", password=True)
                hashed_password = get_password_hash(password)
                users_db[username] = {'password': hashed_password}
                save_users()  # Save the new user to file
                console.print(f"[green]User '{username}' registered successfully![/green]")

            elif auth_choice == "2":
                username = Prompt.ask("Enter username")
                password = Prompt.ask("Enter password", password=True)
                if await agent.login(None, username, password):
                    current_user = username
                    console.print(f"[green]User '{username}' logged in successfully![/green]")
                else:
                    console.print("[red]Invalid credentials or already logged in.[/red]")

            elif auth_choice == "3":
                console.print("[yellow]Exiting...[/yellow]")
                break

        else:
            console.print(f"\n[bold cyan]Expense Tracker Menu for {current_user}:[/bold cyan]")
            console.print("[1] Add Expense")
            console.print("[2] View Total Expenses")
            console.print("[3] Generate Report")
            console.print("[4] Logout")
            console.print("[5] Exit")

            choice = Prompt.ask("Choose an option (1-5)", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                description = Prompt.ask("Enter expense description")
                amount = float(Prompt.ask("Enter expense amount"))
                category = Prompt.ask("Enter expense category")
                await agent.add_expense(None, current_user, description, amount, category)
                console.print(f"[green]Added Expense: Description: {description}, Amount: ${amount}, Category: {category}[/green]")

            elif choice == "2":
                total = await agent.get_total_expenses(None, current_user)
                console.print(f"[yellow]Total Expenses: ${total:.2f}[/yellow]")

            elif choice == "3":
                report = await agent.generate_report(None, current_user)
                display_expense_report(report)

            elif choice == "4":
                await agent.logout(None, current_user)
                current_user = None
                console.print("[yellow]Logged out.[/yellow]")

            elif choice == "5":
                console.print("[yellow]Exiting...[/yellow]")
                break

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")).start()

    # Run the terminal interface
    import asyncio
    asyncio.run(terminal_interface())

# python agent.py