# urls.py
from django.urls import path
from cashflow.views import DataUploadView
from cashflow.views import RealizedAmountCalculator
from cashflow.views import GrossExpectedAmountCalculator
from cashflow.views import RemainingInvestedAmount
from cashflow.views import ClosingDate
from cashflow.views import InvestedAmountCalc
from cashflow.views import TradesDataRetrieval
from cashflow.views import CashflowDataRetrieval
urlpatterns = [
    path('upload/', DataUploadView.as_view(), name='data-upload'),
    path('realized-amount/<str:loan_id>/<str:reference_date>/', RealizedAmountCalculator.as_view(), name='realized-amount'),
    path('gross-amount/<str:loan_id>/<str:reference_date>/', GrossExpectedAmountCalculator.as_view(), name='gross-amount'),
    path('remaing-invested-amount/<str:loan_id>/<str:reference_date>/', RemainingInvestedAmount.as_view(), name='remaining-invested-amount'),
    path('closing-date/<str:loan_id>/<str:reference_date>/', ClosingDate.as_view(), name='closing-date'),
    path('invested-amount/<str:loan_id>/<str:reference_date>/', InvestedAmountCalc.as_view(), name='invested-amount'),
    path('trades-list/', TradesDataRetrieval.as_view(), name='trades-list'),
    path('cashflow-list/', CashflowDataRetrieval.as_view(), name='cashflow-list'),
]


