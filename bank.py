import datetime
import json
import random

class Transaction:
    def __init__(self, date, type, amount, balance_after):
        # Convert datetime to string format for JSON serialization
        self.date = date if isinstance(date, str) else date.strftime("%Y-%m-%d %H:%M:%S")
        self.type = type
        self.amount = amount
        self.balance_after = balance_after

    def __str__(self):
        return f"{self.date} | {self.type} | Amount: ${self.amount} | Balance After: ${self.balance_after}"

    def to_dict(self):
        return {
            "date": self.date,
            "type": self.type,
            "amount": self.amount,
            "balance_after": self.balance_after
        }

    @staticmethod
    def from_dict(data):
        date = datetime.datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")
        return Transaction(date, data["type"], data["amount"], data["balance_after"])

class BankAccount:
    account_counter = 1001  # Static counter for unique account numbers

    def __init__(self, owner, initial_balance=0, account_type="Checking"):
        self.account_number = BankAccount.account_counter
        self.owner = owner
        self.account_type = account_type
        self.balance = initial_balance
        self.transactions = []
        self.interest_rate = 0.01 if account_type == "Savings" else 0
        self.fee = 5 if account_type in ["Checking", "Business"] else 0
        self.pin = self._generate_pin()
        BankAccount.account_counter += 1
        print(f"{account_type} account created for {self.owner} with account number {self.account_number}.")

    def _generate_pin(self):
        return random.randint(1000, 9999)  # Simple 4-digit PIN

    def check_pin(self, pin):
        return self.pin == pin

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(Transaction(datetime.datetime.now(), "Deposit", amount, self.balance))
            print(f"Deposited ${amount}. New balance is ${self.balance}.")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append(Transaction(datetime.datetime.now(), "Withdraw", amount, self.balance))
            print(f"Withdrew ${amount}. New balance is ${self.balance}.")
        else:
            print("Insufficient funds or invalid amount.")

    def transfer(self, amount, recipient_account):
        if 0 < amount <= self.balance:
            self.balance -= amount
            recipient_account.balance += amount
            self.transactions.append(Transaction(datetime.datetime.now(), "Transfer Out", amount, self.balance))
            recipient_account.transactions.append(Transaction(datetime.datetime.now(), "Transfer In", amount, recipient_account.balance))
            print(f"Transferred ${amount} to account {recipient_account.account_number}. New balance is ${self.balance}.")
        else:
            print("Insufficient funds or invalid amount.")

    def apply_interest(self):
        if self.account_type == "Savings" and self.balance > 0:
            interest = self.balance * self.interest_rate
            self.balance += interest
            self.transactions.append(Transaction(datetime.datetime.now(), "Interest", interest, self.balance))
            print(f"Interest of ${interest} applied. New balance is ${self.balance}.")

    def apply_fee(self):
        if self.fee > 0:
            self.balance -= self.fee
            self.transactions.append(Transaction(datetime.datetime.now(), "Monthly Fee", self.fee, self.balance))
            print(f"Monthly fee of ${self.fee} applied. New balance is ${self.balance}.")

    def get_balance(self):
        print(f"Balance for account {self.account_number}: ${self.balance}")
        return self.balance

    def print_statement(self):
        print(f"Transaction statement for account {self.account_number}:")
        for transaction in self.transactions:
            print(transaction)

    def to_dict(self):
        # Convert the account details to a dictionary for JSON storage
        return {
            "account_number": self.account_number,
            "owner": self.owner,
            "account_type": self.account_type,
            "balance": self.balance,
            "transactions": [t.to_dict() for t in self.transactions],
            "interest_rate": self.interest_rate,
            "fee": self.fee,
            "pin": self.pin
        }

    @staticmethod
    def from_dict(data):
        # Create a BankAccount instance from dictionary data
        account = BankAccount(data["owner"], data["balance"], data["account_type"])
        account.account_number = data["account_number"]
        account.transactions = [Transaction.from_dict(t) for t in data["transactions"]]
        account.interest_rate = data["interest_rate"]
        account.fee = data["fee"]
        account.pin = data["pin"]
        return account

def save_accounts(accounts, filename="accounts.json"):
    with open(filename, "w") as file:
        json.dump([account.to_dict() for account in accounts], file)
    print("Accounts saved to file.")

def load_accounts(filename="accounts.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return [BankAccount.from_dict(acc_data) for acc_data in data]
    except FileNotFoundError:
        print("No saved accounts found.")
        return []

# Testing the Enhanced BankAccount Simulator
if __name__ == "__main__":
    # Load accounts from file or create new ones
    accounts = load_accounts()

    # Create new accounts if needed
    account1 = BankAccount("Alice", 1000, "Savings")
    account2 = BankAccount("Bob", 500, "Checking")

    accounts.extend([account1, account2])

    # Perform transactions
    account1.deposit(200)
    account2.withdraw(100)

    # Transfer funds
    account1.transfer(300, account2)

    # Apply monthly updates
    for account in accounts:
        account.apply_interest()
        account.apply_fee()
        account.print_statement()

    # Save accounts back to file
    save_accounts(accounts)
