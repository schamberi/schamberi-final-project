from rest_framework import serializers
from cashflow.models import Trades,Cashflow


class TradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trades
        fields = '__all__'

class CashflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashflow
        fields = '__all__'