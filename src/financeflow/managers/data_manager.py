"""
Data management and business logic module for FinanceFlow.

The DataManager class handles JSON read/write operations, analytical methods,
and CRUD operations for expenses.
"""

import json
import os
from financeflow.models import Expense, Category, Currency
from rich.console import Console
from datetime import datetime
from financeflow.config.logging import LoggerConfig
logger = LoggerConfig.get_file_logger(__name__)

class DataManager:
    """
    Manages persistent data storage, expense operations, and currency configurations.

    Attributes:
        path (str): Absolute file path to the JSON storage file (expenses.json).
    """
    def __init__(self) -> None:
        """
        Initializes the DataManager instance.

        Sets absolute path to `data/expenses.json`.
        Creates directory and empty JSON file if they do not exist.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(current_dir, '..', '..', '..', 'data', 'expenses.json')
        self.path = os.path.abspath(self.path)
        self.console = Console()
        
        directory = os.path.dirname(self.path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)

            logger.info("Created data directory: %s", directory)
            
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump({}, file, indent=4)
                logger.info("Created new expenses storage file: %s", self.path)

    
    def load_file(self) -> dict[str, list[dict] | str]:
        """
        Loads raw structure of the entire JSON file.

        Returns:
            dict[str, list[dict] | str]: Root dictionary stored in the JSON file.
        """

        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    
    def set_currency(self, currency: Currency | None) -> None:
        """
        Saves default application currency to JSON configuration.

        Args:
            currency (Currency | None): Currency enum instance or None to reset.
        """
        file_data = self.load_file()
        file_data['currency'] = currency
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4)
    
    def get_currency(self) -> Currency | None:
        """
        Reads configured default currency from JSON file.

        Returns:
            Currency | None: Configured Currency object, or None if not set.
        """
        file_data = self.load_file()
        if 'currency' not in file_data:
            return None
        elif file_data['currency'] == None:
            return None
        else:
            currency = Currency(file_data['currency'])
            return currency

    def load_all_expenses(self) -> list[dict]:
        """
        Loads and returns the list of all expense dictionaries stored in the file.

        Returns:
            list[dict]: List of expense dictionaries.
        """
        data = self.load_file()
        return data.get('expenses', [])