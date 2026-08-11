# FinanceFlow 💰

FinanceFlow is a command-line personal finance management application written in Python.

The application allows users to manage expenses, set currency preferences, and analyze spending data through an interactive CLI interface.

## Features

- Add new expenses
- Edit existing expenses
- View all expenses
- Filter expenses by month
- Change currency settings
- Find the most common expense category
- Find the month with the highest expenses
- Persistent JSON data storage
- Application logging system

## Technologies

- Python 3.14
- uv - dependency management
- JSON - data storage
- Built-in logging module

## Requirements
- uv

## Installation

### Clone repository

```bash
git clone https://github.com/FilipK721/FinanceFlow.git
cd FinanceFlow
```

### Install all required packages through uv

```bash
uv sync
```

### Run application

```bash
uv run financeflow
```