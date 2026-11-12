"""Export helpers for saving expense data to CSV and XLSX files."""

import csv
from datetime import datetime
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.table import Table, TableStyleInfo

from financeflow.managers.data_manager import DataManager
from financeflow.models import Currency


class ExportManager(DataManager):
    """Export stored expense records to spreadsheet files."""

    def get_default_export_path(self) -> str:
        """Return the default CSV export path for today's export."""
        data_dir = os.path.dirname(self.path)
        export_dir = os.path.join(data_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        filename = f'expenses_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv'
        return os.path.join(export_dir, filename)

    def get_default_xlsx_export_path(self) -> str:
        """Return the default XLSX export path for today's report."""
        data_dir = os.path.dirname(self.path)
        export_dir = os.path.join(data_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        filename = f'expenses_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx'
        return os.path.join(export_dir, filename)

    def export_to_csv(self, file_path: str | None = None) -> str:
        """Export all expenses to a CSV file and return its path.

        Args:
            file_path: Optional explicit destination path. If omitted, a timestamped
                file under the exports directory is used.

        Returns:
            The file path where the CSV was written.

        Raises:
            ValueError: If there are no expenses to export.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')

        if file_path is None:
            file_path = self.get_default_export_path()

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'amount', 'category', 'description', 'id', 'date'])
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense)
        return file_path

    def export_to_xlsx(
        self,
        file_path: str | None = None,
        currency: Currency | None = None,
    ) -> str:
        """Write expenses to a formatted Excel report and return its path.

        Amount cells are numeric for spreadsheet calculations. The total row
        contains an Excel formula, which is calculated when opened in Excel.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')

        report_currency = currency or self.get_currency()
        if report_currency is None:
            raise ValueError('Currency is not configured')

        if file_path is None:
            file_path = self.get_default_xlsx_export_path()

        workbook = Workbook()
        worksheet = workbook.active
        if worksheet is None:
            raise RuntimeError('Workbook has no active worksheet')
        worksheet.title = 'Expenses'
        worksheet.sheet_properties.tabColor = '168C83'
        worksheet.sheet_view.showGridLines = False
        workbook.properties.title = 'FinanceFlow Expense Report'
        workbook.properties.subject = f'Expenses in {report_currency.value}'
        workbook.properties.creator = 'FinanceFlow'

        headers = ['Date', 'Name', 'Category', 'Description', 'ID', 'Amount']
        last_column = len(headers)
        worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_column)
        title = worksheet.cell(row=1, column=1, value='FinanceFlow — Expense Report')
        title.font = Font(name='Aptos Display', size=20, bold=True, color='FFFFFF')
        title.fill = PatternFill('solid', fgColor='123B3A')
        title.alignment = Alignment(vertical='center')
        worksheet.row_dimensions[1].height = 36

        worksheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_column)
        subtitle = worksheet.cell(
            row=2,
            column=1,
            value=(
                f'Currency: {report_currency.value} ({report_currency.symbol})'
                f'    •    Exported: {datetime.now():%Y-%m-%d %H:%M}'
            ),
        )
        subtitle.font = Font(name='Aptos', size=10, color='526B69')

        worksheet['A4'] = 'EXPENSES'
        worksheet['B4'] = len(expenses)
        worksheet['D4'] = 'TOTAL SPENDING'
        worksheet['E4'] = f'=SUM(F7:F{6 + len(expenses)})'
        for cell in (worksheet['A4'], worksheet['B4'], worksheet['D4'], worksheet['E4']):
            cell.fill = PatternFill('solid', fgColor='E6F3F0')
            cell.font = Font(name='Aptos', bold=True, color='123B3A')
            cell.alignment = Alignment(vertical='center')
        worksheet['E4'].number_format = self._xlsx_amount_format(report_currency)
        worksheet.row_dimensions[4].height = 25

        header_row = 6
        for column, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=header_row, column=column, value=header)
            cell.font = Font(name='Aptos', bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='168C83')
            cell.alignment = Alignment(vertical='center')
        worksheet.row_dimensions[header_row].height = 24

        first_data_row = header_row + 1
        for row_number, expense in enumerate(expenses, start=first_data_row):
            values = (
                expense['date'],
                expense['name'],
                expense['category'],
                expense['description'],
                expense['id'],
                expense['amount'],
            )
            for column, value in enumerate(values, start=1):
                cell = worksheet.cell(row=row_number, column=column, value=value)
                cell.font = Font(name='Aptos', size=10, color='253B3A')
                if column == 1:
                    cell.number_format = 'dd-mmm-yyyy'
                elif column == 5:
                    cell.alignment = Alignment(horizontal='center')
                elif column == 6:
                    cell.number_format = self._xlsx_amount_format(report_currency)
                    cell.alignment = Alignment(horizontal='right')

        last_data_row = first_data_row + len(expenses) - 1
        table = Table(
            displayName='ExpenseRecords',
            ref=f'A{header_row}:F{last_data_row}',
        )
        table.tableStyleInfo = TableStyleInfo(
            name='TableStyleMedium4',
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        worksheet.add_table(table)

        total_row = last_data_row + 1
        worksheet.cell(row=total_row, column=5, value='TOTAL')
        total = worksheet.cell(
            row=total_row,
            column=6,
            value=f'=SUM(F{first_data_row}:F{last_data_row})',
        )
        for cell in (worksheet.cell(row=total_row, column=5), total):
            cell.font = Font(name='Aptos', bold=True, color='123B3A')
            cell.fill = PatternFill('solid', fgColor='D5EBE6')
        total.number_format = self._xlsx_amount_format(report_currency)

        for column_name, width in {
            'A': 16,
            'B': 26,
            'C': 20,
            'D': 38,
            'E': 10,
            'F': 19,
        }.items():
            worksheet.column_dimensions[column_name].width = width
        worksheet.freeze_panes = 'A7'
        worksheet.print_title_rows = f'{header_row}:{header_row}'
        worksheet.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        worksheet.page_setup.fitToWidth = 1
        worksheet.page_setup.fitToHeight = 0

        workbook.save(file_path)
        return file_path

    @staticmethod
    def _xlsx_amount_format(currency: Currency) -> str:
        """Return an Excel numeric format with the currency's precision."""
        decimals = currency.decimal_places
        number_pattern = '#,##0' if decimals == 0 else '#,##0.' + ('0' * decimals)
        symbol = currency.symbol.replace('"', '""')
        return f'{number_pattern} "{symbol}";[Red]-{number_pattern} "{symbol}"'