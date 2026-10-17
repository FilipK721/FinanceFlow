"""Entry point for the FinanceFlow command-line application."""

from financeflow.cli import run_cli


def main() -> None:
    """Start the FinanceFlow CLI."""
    run_cli()

if __name__ == '__main__':
    main()
