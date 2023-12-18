import os
import django
import pandas as pd
from django.conf import settings
from django.utils.dateparse import parse_date
from datetime import datetime
from decimal import Decimal
from django.db.models import F
from django.db.models import Subquery, OuterRef

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoassignment.settings')

# Configure Django
django.setup()
from cashflow.models import Trades, Cashflow

class CashflowCalculator:
    def __init__(self, loanID, reference_date):
        self.loanID = loanID
        self.reference_date = reference_date

    def get_realized_amount(self):
        realized_amount = 0
        cashflows = Cashflow.objects.filter(cashflow_type='repayment', loan_id=self.loanID).values('cashflow_date', 'cashflow_amount')
        for cashflow in cashflows:
            if cashflow['cashflow_date'] <= self.reference_date:
                realized_amount += cashflow['cashflow_amount']
        return realized_amount

    def invested_amount_calculation(self):
        subquery = Cashflow.objects.filter(loan_id=OuterRef('loan_id'), cashflow_type='funding').values('cashflow_type', 'cashflow_amount')
        trades_cashflow_join = (
            Trades.objects.filter(loan_id=self.loanID)
            .annotate(
                cashflow_type=Subquery(subquery.values('cashflow_type')),
                cashflow_amount=Subquery(subquery.values('cashflow_amount'))
            )
            .values('loan_id', 'investment_date', 'maturity_date', 'interest_rate', 'cashflow_type', 'cashflow_amount')
        )
        invested_amount = 0
        for trade_cashflows in trades_cashflow_join:
            if trade_cashflows['investment_date'] <= self.reference_date:
                invested_amount += abs(trade_cashflows['cashflow_amount'])
        return invested_amount

    def gross_expected_amount(self):
        #doing a join with a subquery because due to pc issues couldn't define dk on the models, found this alternative
        subquery = Cashflow.objects.filter(loan_id=OuterRef('loan_id'), cashflow_type='funding').values('cashflow_type', 'cashflow_amount')
        trades_cashflow_join = (
            Trades.objects.filter(loan_id=self.loanID)
            .annotate(
                cashflow_type=Subquery(subquery.values('cashflow_type')),
                cashflow_amount=Subquery(subquery.values('cashflow_amount'))
            )
            .values('loan_id', 'investment_date', 'maturity_date', 'interest_rate', 'cashflow_type', 'cashflow_amount')
        )

        for trade_cashflows in trades_cashflow_join:
            daily_interest_rate = trade_cashflows['interest_rate'] / 365
            passed_days = (self.reference_date - trade_cashflows['investment_date']).days
            daily_interest_amount = self.invested_amount_calculation() * trade_cashflows['interest_rate']
            gross_expected_interest_amount = daily_interest_amount * passed_days

        return self.invested_amount_calculation() + gross_expected_interest_amount

    def get_remaining_invested_amount(self):
        realized_amount = self.get_realized_amount()
        return self.invested_amount_calculation() - realized_amount

    #call the class
    # Get user input for loanID
loanID = input("Enter the loan ID in this alphanumerical format(xxxxx_xx_xxxxxxx): ")

# Get user input for reference_date
reference_date_str = input("Enter the reference date (YYYY-MM-DD): ")

# Validate and parse the input for reference_date
try:
    reference_date = datetime.strptime(reference_date_str, "%Y-%m-%d").date()
except ValueError:
    print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
    exit()

# Create an instance of CashflowCalculator
calculator = CashflowCalculator(loanID, reference_date)

# Call the method and display the result
realized_amount = calculator.get_realized_amount()
print(f"The realized amount is: {realized_amount}")
remaining_invested_amount = calculator.get_remaining_invested_amount()
print(f"The remaining invested amount is: {remaining_invested_amount}")
grossExpected_amount = calculator.gross_expected_amount()
print(f"The gross expected amount is: {grossExpected_amount}")
