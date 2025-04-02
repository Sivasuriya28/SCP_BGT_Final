import uuid
import logging
from rest_framework import serializers
from .models import Expense, Budget

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExpenseSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=False, allow_null=True)
    category = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(allow_blank=True, required=False)
    date = serializers.DateField(format="%Y-%m-%d")

    # ✅ These two are now optional, not just read-only
    converted_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    converted_currency = serializers.CharField(required=False, allow_null=True)

    def create(self, validated_data):
        if not validated_data.get('transaction_id'):
            validated_data['transaction_id'] = str(uuid.uuid4())

        expense = Expense(**validated_data)
        expense.save()
        return expense


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'allocated_amount']

    def create(self, validated_data):
        budget = Budget(**validated_data)
        budget.save()
        return budget
