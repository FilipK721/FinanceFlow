# 💰 FinanceFlow

**FinanceFlow** is an interactive command-line application for managing personal finances — track expenses, set budget limits, analyze your spending with terminal charts, and export your data, all from a colorful terminal interface.

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
- Terminal charts powered by [`plotext`](https://github.com/piccolomo/plotext):
  - spending by category (bar chart)
  - monthly spending trend (line chart, in chronological order)

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
- Persistent storage in a local **SQLite** database via **SQLAlchemy 2.0** — no database server or setup required
- Database engine is created lazily (on first use), so importing the package never touches your data file
- Managers accept an injectable database session, which keeps tests isolated (in-memory SQLite)
- Full application logging (console + rotating log files)
- Static type checking with `mypy`
- Built with [`rich`](https://github.com/Textualize/rich) for a polished terminal UI

---

## 🛠️ Technologies

| | |
|---|---|
| **Language** | Python 3.14 |
| **Dependency management** | [uv](https://docs.astral.sh/uv/) |
| **Terminal UI** | [rich](https://github.com/Textualize/rich) |
| **Charts** | [plotext](https://github.com/piccolomo/plotext) |
| **Logging** | [colorlog](https://github.com/borntyping/python-colorlog) + built-in `logging` |
| **Storage** | SQLite via [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 |
| **Type checking** | [mypy](https://mypy-lang.org/) |
| **Testing** | pytest, pytest-cov |

---

## 📦 Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [git](https://git-scm.com)

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

Your data is stored locally in `data/financeflow.db` (created automatically on first run and excluded from version control).

---

## 🖥️ Usage

On first run, you'll be asked to choose a currency. From there, the main menu gives you access to everything:

- 💰 Expenses — add, view, edit, delete
- 📊 Analytics — spending insights and charts
- 🎯 Budget — set limits, monitor spending
- ⚙️ Settings — change currency
- 📤 Export — export your data to CSV

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

Tests run against an in-memory SQLite database, so they never touch your real data.

---

## 🔎 Type checking

```bash
uv run mypy src
```

---

## 📁 Project structure

```
FinanceFlow/
├── src/financeflow/
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── models.py                  # Expense, Category, Currency (domain models)
│   ├── views.py                   # Terminal UI (rich) and charts (plotext)
│   ├── config/
│   │   ├── __init__.py
│   │   └── logging.py             # Logging setup
│   ├── db/
│   │   ├── engine.py              # Lazy SQLAlchemy engine & session factory
│   │   └── models.py              # Database tables (expenses, category limits, settings)
│   └── managers/
│       ├── data_manager.py        # Session handling, currency, loading expenses
│       ├── expense_manager.py     # Expense CRUD
│       ├── analytics_manager.py   # Spending insights & chart data
│       ├── budget_manager.py      # Limits & budget tracking
│       └── export_manager.py      # CSV export
├── tests/unit/
│   ├── conftest.py                # In-memory DB session & manager fixtures
│   ├── test_analytics_manager.py
│   ├── test_budget_manager.py
│   ├── test_data_manager.py
│   ├── test_expense_manager.py
│   ├── test_export_manager.py
│   ├── test_models.py
│   └── test_views.py
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

- [x] Migrate storage from JSON to SQLite via SQLAlchemy
- [x] Charts: spending by category and monthly trend
- [ ] Recurring expenses / subscriptions
- [ ] Import expenses from CSV
- [ ] Search and sort expenses
- [ ] Switch to MySQL/PostgreSQL (SQLAlchemy makes this a connection-string change plus minor type tweaks)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).