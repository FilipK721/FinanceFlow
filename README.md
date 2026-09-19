# 💰 FinanceFlow

**FinanceFlow** is an interactive command-line application for managing personal finances — track expenses, set budget limits, analyze your spending, and export your data, all from a colorful terminal interface.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.14-blue.svg" alt="Python 3.14">
  <img src="https://img.shields.io/badge/dependency--manager-uv-purple.svg" alt="uv">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
</p>

---

## ✨ Features

### 💸 Expense tracking
- Add, edit, and delete expenses
- Categorize each expense (Food, Groceries, Health, Entertainment, Bills, Education, Fuel, Other)
- View all expenses in a clean, colorized table
- Filter expenses by month

### 📊 Analytics
- Find your most common expense category
- Identify the month with the highest spending
- Browse expenses month by month

### 🎯 Budgeting
- Set a global monthly spending limit
- Set individual limits **per category** (e.g. cap "Entertainment" separately from "Food")
- Live limit tracker shown right next to the main menu — see at a glance how close you are to any limit
- Automatic warnings at 80% and 100%+ of a limit

### 📤 Data export
- Export all expenses to a CSV file
- Files are saved with an automatic, date-stamped filename — or provide your own path

### ⚙️ Settings
- Switch between currencies (Euro, Dollars, Pounds, Yen, Złoty)

### 🗂️ Under the hood
- Persistent JSON-based storage — no database setup required
- Full application logging (console + rotating log files)
- Built with [`rich`](https://github.com/Textualize/rich) for a polished terminal UI

---

## 🛠️ Technologies

| | |
|---|---|
| **Language** | Python 3.14 |
| **Dependency management** | [uv](https://docs.astral.sh/uv/) |
| **Terminal UI** | [rich](https://github.com/Textualize/rich) |
| **Logging** | [colorlog](https://github.com/borntyping/python-colorlog) + built-in `logging` |
| **Storage** | JSON |
| **Testing** | pytest, pytest-cov |

---

## 📦 Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

---

## 🚀 Installation

**1. Clone the repository**
```bash
git clone https://github.com/FilipK721/FinanceFlow.git
cd FinanceFlow
```

**2. Install dependencies**
```bash
uv sync
```

**3. Run the app**
```bash
uv run financeflow
```

---

## 🖥️ Usage

On first run, you'll be asked to choose a currency. From there, the main menu gives you access to everything:
💰 Expenses — add, view, edit, delete
📊 Analytics — spending insights
🎯 Budget — set limits, monitor spending
⚙️ Settings — change currency
📤 Export — export your data to CSV
🔚 Exit

Your current budget limits (both global and per-category) are always visible right next to the menu, so you always know where you stand.

---

## 🧪 Running tests

```bash
uv run pytest
```

With coverage:
```bash
uv run pytest --cov=financeflow
```

---

## 📁 Project structure

```
FinanceFlow/
├── src/financeflow/
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── models.py                  # Expense, Category, Currency
│   ├── views.py                   # Terminal UI (rich)
│   ├── config/
│   │   ├── __init__.py
│   │   └── logging.py             # Logging setup
│   └── managers/
│       ├── data_manager.py        # JSON read/write
│       ├── expense_manager.py     # Expense CRUD
│       ├── analytics_manager.py   # Spending insights
│       ├── budget_manager.py      # Limits & budget tracking
│       └── export_manager.py      # CSV export
├── tests/unit/
│   ├── conftest.py
│   ├── test_analytics_manager.py
│   ├── test_budget_manager.py
│   ├── test_data_manager.py
│   ├── test_expense_manager.py
│   ├── test_export_manager.py
│   └── test_models.py
├── notebook.py
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

- [ ] Import expenses from CSV
- [ ] Recurring expenses / subscriptions
- [ ] Search and sort expenses
- [ ] Migrate storage to MySQL/PostgreSQL via SQLAlchemy

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).