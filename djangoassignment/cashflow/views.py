import pandas as pd
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Trades, Cashflow
from cashflow.serializers import TradesSerializer, CashflowSerializer
from datetime import datetime
from decimal import Decimal
from django.db.models import Subquery, OuterRef

class DataUploadView(APIView):

    def post(self, request, *args, **kwargs):
        try:
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
                        
                        
                        print(f"Parsed Investment Date: {investment_date}, Parsed Maturity Date: {maturity_date}")

                        Trades.objects.create(
                            loan_id=row['loan_id'],
                            investment_date=investment_date,
                            maturity_date=maturity_date,
                            interest_rate=interest_rate_value
                        )
                    except Exception as e:
                        print(f"Error importing trade at index {index}: {e}")

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

            import_trades()
            import_cashflow()

            # Assuming everything is successful, return a success response
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in DataUploadView post method: {e}")
            # If an error occurs, return an error response
            return Response({'message': 'An error occurred during data import'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#all calculations

class InvestmentsCalculations:

    @staticmethod
    def get_realized_amount(loan_id, reference_date):
        realized_amount = 0
        cashflows = Cashflow.objects.filter(cashflow_type='repayment', loan_id=loan_id).values('cashflow_date', 'cashflow_amount')
        for cashflow in cashflows:
            if cashflow['cashflow_date'] <= reference_date:
                realized_amount += cashflow['cashflow_amount']
        return realized_amount

    @staticmethod
    def invested_amount_calculation(loan_id, reference_date):
        subquery = Cashflow.objects.filter(loan_id=OuterRef('loan_id'), cashflow_type='funding').values('cashflow_type', 'cashflow_amount')
        trades_cashflow_join = (
            Trades.objects.filter(loan_id=loan_id)
            .annotate(
                cashflow_type=Subquery(subquery.values('cashflow_type')[:1]),
                cashflow_amount=Subquery(subquery.values('cashflow_amount')[:1])
            )
            .values('loan_id', 'investment_date', 'maturity_date', 'interest_rate', 'cashflow_type', 'cashflow_amount')
        )
        invested_amount = 0
        for trade_cashflows in trades_cashflow_join:
            if trade_cashflows['investment_date'] <= reference_date:
                invested_amount += abs(trade_cashflows['cashflow_amount'])
        return invested_amount

    @staticmethod
    def gross_expected_amount(loan_id, reference_date):
        subquery = Cashflow.objects.filter(loan_id=OuterRef('loan_id'), cashflow_type='funding').values('cashflow_type', 'cashflow_amount')
        trades_cashflow_join = (
            Trades.objects.filter(loan_id=loan_id)
            .annotate(
                cashflow_type=Subquery(subquery.values('cashflow_type')[:1]),
                cashflow_amount=Subquery(subquery.values('cashflow_amount')[:1])
            )
            .values('loan_id', 'investment_date', 'maturity_date', 'interest_rate', 'cashflow_type', 'cashflow_amount')
        )

        gross_expected_interest_amount = 0
        for trade_cashflows in trades_cashflow_join:
            daily_interest_rate = trade_cashflows['interest_rate'] / 365
            passed_days = (reference_date - trade_cashflows['investment_date']).days
            daily_interest_amount = InvestmentsCalculations.invested_amount_calculation(loan_id, reference_date) * daily_interest_rate
            gross_expected_interest_amount += daily_interest_amount * passed_days

        return InvestmentsCalculations.invested_amount_calculation(loan_id, reference_date) + gross_expected_interest_amount

    @staticmethod
    def get_remaining_invested_amount(loan_id, reference_date):
        realized_amount = InvestmentsCalculations.get_realized_amount(loan_id, reference_date)
        return InvestmentsCalculations.invested_amount_calculation(loan_id, reference_date) - realized_amount

    @staticmethod
    def get_closing_date(loan_id,reference_date):
        maturity_date=maturity_date = Trades.objects.filter(loan_id=loan_id).values_list('maturity_date', flat=True).first()
        if InvestmentsCalculations.get_realized_amount(loan_id,reference_date) >= InvestmentsCalculations.gross_expected_amount(loan_id,maturity_date):
            return maturity_date
        return None

#realized_amount_calculation
class RealizedAmountCalculator(APIView):
    def get(self, request, loan_id, reference_date, *args, **kwargs):
        try:
           
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'message': 'Invalid date format. Please enter the date in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

            
            realized_amount = InvestmentsCalculations.get_realized_amount(loan_id, reference_date)

            
            response_data = {'realized_amount': realized_amount}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Gross Expected Amount
class GrossExpectedAmountCalculator(APIView):
    def get(self, request, loan_id, reference_date, *args, **kwargs):
        try:
            
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'message': 'Invalid date format. Please enter the date in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

            
            gross_expected_amount = InvestmentsCalculations.gross_expected_amount(loan_id, reference_date)

            
            response_data = {'gross_expected_amount': gross_expected_amount}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#remaining amount
class RemainingInvestedAmount(APIView):
    def get(self, request, loan_id, reference_date, *args, **kwargs):
        try:
            
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'message': 'Invalid date format. Please enter the date in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

            
            remaining_invested_amount = InvestmentsCalculations.get_remaining_invested_amount(loan_id, reference_date)

            
            response_data = {'remaining_invested_amount': remaining_invested_amount}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#closing date       
class ClosingDate(APIView):
    def get(self, request, loan_id, reference_date, *args, **kwargs):
        try:
           
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'message': 'Invalid date format. Please enter the date in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

            closingDate = InvestmentsCalculations.get_closing_date(loan_id, reference_date)
            response_data = {'closing_date': closingDate}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Invested amount
class InvestedAmountCalc(APIView):
    def get(self, request, loan_id, reference_date, *args, **kwargs):
        try:
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'message': 'Invalid date format. Please enter the date in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

            invested_amount = InvestmentsCalculations.invested_amount_calculation(loan_id, reference_date)

            response_data = {'invested_amount': invested_amount}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Trades
class TradesDataRetrieval(APIView):
    def get(self, request, *args, **kwargs):
        try:
            
            trades_data = Trades.objects.all()

            
            trades_list = [
                {
                    'loan_id': trade.loan_id,
                    'investment_date': trade.investment_date,
                    'maturity_date': trade.maturity_date,
                    'interest_rate': float(trade.interest_rate),
                }
                for trade in trades_data
            ]

            response_data = {'trades': trades_list}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#cashflow
class CashflowDataRetrieval(APIView):
    def get(self, request, *args, **kwargs):
        try:
            cashflow_data = Cashflow.objects.all()

            cashflow_list = [
                {
                    'cashflow_id': cashflow.cashflow_id,
                    'loan_id': cashflow.loan_id,
                    'cashflow_date': cashflow.cashflow_date,
                    'cashflow_currency': cashflow.cashflow_currency,
                    'cashflow_type': cashflow.cashflow_type,
                    'cashflow_amount': float(cashflow.cashflow_amount),
                }
                for cashflow in cashflow_data
            ]

            response_data = {'cashflows': cashflow_list}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)