import uuid
import logging
import requests
import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Expense, Budget
from .serializers import ExpenseSerializer, BudgetSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

# Logger Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants
CURRENCY_CONVERTER_API_URL = "https://2430zel9za.execute-api.eu-west-1.amazonaws.com/prod/convert"
DEFAULT_BASE_CURRENCY = "EUR"


class ExpenseViewSet(viewsets.ViewSet):
    """
    Handles listing and creating expenses.
    """

    def list(self, request):
        """
        Returns all stored expenses.
        """
        expenses = Expense.get_all()
        return Response(expenses)

    def create(self, request):
        """
        Creates a new expense, performs currency conversion if needed,
        and saves the converted data.
        """
        logger.setLevel(logging.DEBUG)
        data = request.data.copy()
        original_currency = data.get("currency", DEFAULT_BASE_CURRENCY)
        data["currency"] = original_currency  # Ensure it's saved

        logger.debug(f"Incoming expense data: {data}")

        # Generate transaction ID if not provided
        if not data.get('transaction_id'):
            data['transaction_id'] = str(uuid.uuid4())

        # Default values
        data["converted_amount"] = None
        data["converted_currency"] = None

        # Handle currency conversion
        if original_currency.upper() != DEFAULT_BASE_CURRENCY:
            try:
                payload = {
                    "amount": float(data["amount"]),
                    "from_currency": original_currency.upper(),
                    "to_currency": DEFAULT_BASE_CURRENCY
                }
                headers = {"Content-Type": "application/json"}

                logger.debug(f"Sending conversion request: {payload}")
                response = requests.post(CURRENCY_CONVERTER_API_URL, json=payload, headers=headers)
                logger.debug(f"Conversion response: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    result = response.json()
                    data["converted_amount"] = result.get("converted_amount")
                    data["converted_currency"] = DEFAULT_BASE_CURRENCY
                    logger.debug(f"Converted: {data['converted_amount']} {DEFAULT_BASE_CURRENCY}")
                else:
                    logger.warning("Conversion failed. Skipping conversion fields.")
            except Exception as e:
                logger.error(f"Currency conversion error: {str(e)}")

        else:
            # If currency is EUR, use original amount directly
            data["converted_amount"] = data["amount"]
            data["converted_currency"] = DEFAULT_BASE_CURRENCY

        # Save to DB via serializer
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning("Validation failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetViewSet(viewsets.ViewSet):
    """
    Handles listing, creating, and retrieving budget records.
    """

    def list(self, request):
        """
        Returns all stored budgets.
        """
        budgets = Budget.get_all()
        return Response(budgets)

    def create(self, request):
        """
        Creates a new budget entry.
        """
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieves budget summary for a specific category.
        """
        budget_status = Budget.get_budget_status(pk)
        if budget_status:
            return Response(budget_status)
        return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)


EMAIL_API_URL = "https://574zxm1da6.execute-api.eu-west-1.amazonaws.com/default/x23271281-EmailSenderAPI"

class SummaryView(APIView):
    def get(self, request):
        summary = []
        budgets = Budget.get_all()

        for b in budgets:
            status_info = Budget.get_budget_status(b["category"])
            if status_info:
                summary.append({
                    "id": b["budget_id"],
                    "category": b["category"],
                    "allocated_amount": float(b["allocated_amount"]),
                    "spent_amount": float(status_info["spent_amount"]),
                    "remaining_amount": float(status_info["remaining_amount"]),
                    "status": status_info["status"]
                })

                # Send email if over budget
                if status_info["status"] == "Over Budget":
                    try:
                        email_data = {
                            "email": getattr(settings, "DEFAULT_ALERT_EMAIL", "youremail@example.com"),
                            "subject": f"Budget Alert: {b['category']}",
                            "content": (
                                f"You are over budget for category '{b['category']}'.\n\n"
                                f"Allocated: €{b['allocated_amount']}\n"
                                f"Spent: €{status_info['spent_amount']}\n"
                                f"Over by: €{status_info['spent_amount'] - b['allocated_amount']}"
                            )
                        }
                        requests.post(EMAIL_API_URL, json=email_data)
                    except Exception as e:
                        print(f"Email send failed for {b['category']}: {e}")

        return Response(summary, status=status.HTTP_200_OK)

@csrf_exempt
def convert_currency_view(request):
    """
    Supports both GET (query params) and POST (JSON) for currency conversion.
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            amount = float(data["amount"])
            from_currency = data["from_currency"]
            to_currency = data["to_currency"]

        elif request.method == 'GET':
            amount = float(request.GET.get("amount"))
            from_currency = request.GET.get("from_currency")
            to_currency = request.GET.get("to_currency")
        else:
            return JsonResponse({"error": "Invalid request method"}, status=400)

        payload = {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency
        }

        response = requests.post(
            CURRENCY_CONVERTER_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class BudgetCreateAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            category = data.get('category')
            allocated_amount = data.get('allocated_amount')

            if not category or allocated_amount is None:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            budget = Budget(category=category, allocated_amount=allocated_amount)
            budget.save()
            return Response({"message": "Budget saved successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)