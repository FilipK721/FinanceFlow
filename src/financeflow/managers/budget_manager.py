"""Budget-limit management for the FinanceFlow application."""

from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.models import Category
from financeflow.db.models import SettingRow, CategoryLimitRow
from datetime import date


class BudgetManager(AnalyticsManager):
    """Manage overall and per-category budget limits and their usage percentages."""

    def set_limit(self, limit: float) -> None:
        """Save the monthly overall spending limit.

        Args:
            limit: Maximum allowed total spending for the current period.
        """
        existing = self.session.get(SettingRow, 'limit')
        if existing:
            existing.value = str(limit)
        else:
            new_limit = SettingRow(key='limit', value=str(limit))
            self.session.add(new_limit)

        self.session.commit()

    def get_limit(self) -> float | None:
        """Return the configured overall spending limit, if any."""
        existing = self.session.get(SettingRow, 'limit')
        if existing is not None:
            return float(existing.value)
        return None

    def set_limit_for_category(self, category: Category, limit: float) -> None:
        """Save a spending cap for a specific expense category.

        Args:
            category: The category for which the limit applies.
            limit: Maximum allowed spending for that category.
        """
        existing = self.session.get(CategoryLimitRow, category.value)

        if existing is not None:
            existing.limit = limit
        else:
            new_limit = CategoryLimitRow(category=category.value, limit=limit)
            self.session.add(new_limit)

        self.session.commit()

    def get_category_limit(self, category: Category) -> float | None:
        """Return the spending limit configured for a given category.

        Args:
            category: Category to look up.

        Returns:
            The category limit as a float, or None if no limit is set.
        """
        existing = self.session.get(CategoryLimitRow, category.value)
        if existing is None:
            return None
        return float(existing.limit)

    def delete_category_limit(self, category: Category) -> None:
        """Remove the limit configured for a specific category.

        Args:
            category: Category whose limit should be deleted.

        Raises:
            ValueError: If no limit exists for the given category.
        """
        existing = self.session.get(CategoryLimitRow, category.value)

        if existing is not None:
            self.session.delete(existing)
        else:
            raise ValueError(f'Limit for \'{category}\' not found')

        self.session.commit()

    def make_limits_check(self) -> bool:
        """Check whether spending has exceeded any configured limits.

        Returns:
            True if all configured limits are still under their thresholds,
            otherwise False.
        """
        if self.get_limit() is not None:
            if self.percentage_of_the_limit() >= 100:
                return False
        for category in Category:
            if self.get_category_limit(category) is not None:
                if self.percentage_of_category_limit(category) >= 100:
                    return False
        return True

    def delete_limit(self) -> None:
        """Remove the global budget limit.

        Raises:
            ValueError: If no global limit is currently configured.
        """
        existing = self.session.get(SettingRow, 'limit')

        if existing is not None:
            self.session.delete(existing)
        else:
            raise ValueError('Limit not found')

        self.session.commit()

    def percentage_of_the_limit(self) -> int:
        """Calculate how much of the global limit has been used this month.

        Returns:
            Percentage of the configured total limit currently spent.
        """
        today = date.today()
        all_expenses = self.all_expenses_from_a_given_month(today.month, today.year)
        limit = self.get_limit()
        if limit is None or limit == 0:
            return 0
        total_amount = sum(expense['amount'] for expense in all_expenses)
        return int(total_amount / limit * 100)

    def percentage_of_category_limit(self, category: Category) -> int:
        """Calculate how much of a category limit has been used this month.

        Args:
            category: The category to evaluate.

        Returns:
            Percentage of the configured category limit currently spent.
        """
        today = date.today()
        all_expenses = self.all_expenses_from_a_given_month(today.month, today.year)
        limit = self.get_category_limit(category)
        if limit is None or limit == 0:
            return 0
        total_amount = sum(expense['amount'] for expense in all_expenses if expense['category'] == category)
        return int(total_amount / limit * 100)