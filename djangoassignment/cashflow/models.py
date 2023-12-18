from django.db import models

class Trades(models.Model):
    loan_id = models.CharField(max_length=20)
    investment_date = models.DateField(null=True)
    maturity_date = models.DateField(null=True)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Loan ID: {self.loan_id}, Investment Date: {self.formatted_investment_date()}, Maturity Date: {self.formatted_maturity_date()}, Interest Rate: {self.interest_rate}%"

class Cashflow(models.Model):
    cashflow_id = models.CharField(max_length=20) 
    loan_id = models.CharField(max_length=20) # Foreign key reference
    cashflow_date = models.DateField(null=True)
    cashflow_currency = models.CharField(max_length=3)
    cashflow_type = models.CharField(max_length=9, choices=[('funding', 'Funding'), ('repayment', 'Repayment')])
    cashflow_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.cashflow_id} - {self.cashflow_amount} {self.cashflow_currency} - {self.cashflow_type}, Cashflow Date: {self.formatted_cashflow_date()}"



