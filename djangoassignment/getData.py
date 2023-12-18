import os
import django
import pandas as pd
from django.conf import settings
from django.utils.dateparse import parse_date
from datetime import datetime
from decimal import Decimal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoassignment.settings')

# Configure Django
django.setup()

from cashflow.models import Trades, Cashflow


trades_file_path = r'cashflow\static_data\trades.xlsx'
cashflow_file_path = r'cashflow\static_data\cash_flows.xlsx'
trades_data = pd.read_excel(trades_file_path)
cashflow_data = pd.read_excel(cashflow_file_path)

def import_trades():
    for index, row in trades_data.iterrows():
        try:
            # Print the date strings and their formats
            print(f"Original Investment Date: {row['investment_date']}, Original Maturity Date: {row['maturity_date']}")
            
            # Extract the numeric value from the percentage string
            interest_rate_str = str(row['interest_rate'])
            interest_rate_value = Decimal(interest_rate_str.rstrip('%'))

            # Convert dates to the format MM/DD/YYYY
            investment_date = datetime.strptime(row['investment_date'], '%d/%m/%Y')
            maturity_date = datetime.strptime(row['maturity_date'], '%d/%m/%Y')
            
            # Print the parsed dates - to check if the date is parsing correctly 
            print(f"Parsed Investment Date: {investment_date}, Parsed Maturity Date: {maturity_date}")

            Trades.objects.create(
                loan_id=row['loan_id'],
                investment_date=investment_date,
                maturity_date=maturity_date,
                interest_rate=interest_rate_value
            )
        except Exception as e:
            print(f"Error importing trade at index {index}: {e}")

import_trades()



def import_cashflow():
    
    for index, row in cashflow_data.iterrows():
        try:
           
            cashflow_date = datetime.strptime(row['cashflow_date'], '%d/%m/%Y')

            # Clean up cashflow_amount by removing non-numeric characters
            cashflow_amount_str = str(row['amount']).replace(' ', '').replace('“', '').replace('”', '').replace('', '').replace(',', '')
            cashflow_amount = Decimal(cashflow_amount_str)

            Cashflow.objects.create(
                cashflow_id=row['cashflow_id'],
                loan_id=row['loan_id'],
                cashflow_date=cashflow_date,
                cashflow_currency=row['cashflow_currency'],
                cashflow_type=row['cashflow_type'],
                cashflow_amount=cashflow_amount
            )
        except Exception as e:
            print(f"Error importing cashflow at index {index}: {e}")
            
import_cashflow()
