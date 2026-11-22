import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense, Payment
from .forms import ExpenseForm
from .serializers import ExpenseSerializer
from .mpesa import initiate_stk_push

def home(request):
    expenses = Expense.objects.all().order_by("-date", "-created_at")

    total = sum(expense.amount for expense in expenses)

    context = {
        "expenses": expenses,
        "total": total,
    }

    return render(request, "expenses/home.html", context)


def expense_list(request):
    expenses = Expense.objects.all().order_by("-date", "-created_at")

    return render(
        request,
        "expenses/expense_list.html",
        {"expenses": expenses},
    )


def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("expense_list")
    else:
        form = ExpenseForm()

    return render(
        request,
        "expenses/add_expense.html",
        {"form": form},
    )


class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Expense.objects.all().order_by("-date", "-created_at")
    serializer_class = ExpenseSerializer

class ExpenseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class PaymentAPIView(APIView):

    def post(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")

        if not phone_number:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not amount:
            return Response(
                {"error": "Amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            return Response(
                {"error": "Amount must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            phone_number=phone_number,
            amount=amount,
        )

        try:
            response = initiate_stk_push(
                phone_number,
                amount,
            )

            payment.checkout_request_id = response.get(
                "CheckoutRequestID"
            )

            payment.merchant_request_id = response.get(
                "MerchantRequestID"
            )

            payment.result_description = response.get(
                "CustomerMessage"
            )

            payment.save()

            return Response(
                {
                    "message": "STK Push initiated successfully.",
                    "payment_id": payment.id,
                    "response": response,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:

            payment.status = "Failed"
            payment.result_description = str(error)
            payment.save()

            return Response(
                {
                    "error": "Unable to initiate M-Pesa payment.",
                    "details": str(error),
                    "payment_id": payment.id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class PaymentAPIView(APIView):

    def post(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")

        if not phone_number or not amount:
            return Response(
                {
                    "error": "Phone number and amount are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)

            if amount <= 0:
                return Response(
                    {
                        "error": "Amount must be greater than zero."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Invalid amount."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            phone_number=phone_number,
            amount=amount,
            status="Pending",
        )

        try:
            mpesa_response = initiate_stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference=f"CampusPay-{payment.id}",
                description="CampusPay Student Payment",
            )

            payment.checkout_request_id = mpesa_response.get(
                "CheckoutRequestID"
            )

            payment.merchant_request_id = mpesa_response.get(
                "MerchantRequestID"
            )

            payment.result_description = mpesa_response.get(
                "CustomerMessage"
            )

            payment.save()

            return Response(
                {
                    "message": "STK Push initiated successfully.",
                    "payment_id": payment.id,
                    "mpesa_response": mpesa_response,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            payment.status = "Failed"
            payment.result_description = str(error)
            payment.save()

            return Response(
                {
                    "error": "Failed to initiate M-Pesa payment.",
                    "details": str(error),
                    "payment_id": payment.id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only POST requests are allowed."
            },
            status=405,
        )

    try:
        data = json.loads(request.body)

        callback = data.get("Body", {}).get(
            "stkCallback", {}
        )

        checkout_request_id = callback.get(
            "CheckoutRequestID"
        )

        result_code = callback.get("ResultCode")
        result_description = callback.get(
            "ResultDesc"
        )

        payment = Payment.objects.filter(
            checkout_request_id=checkout_request_id
        ).first()

        if payment:

            payment.result_description = (
                result_description
            )

            if result_code == 0:

                payment.status = "Completed"

                callback_metadata = callback.get(
                    "CallbackMetadata", {}
                )

                items = callback_metadata.get(
                    "Item", []
                )

                for item in items:

                    if item.get("Name") == "MpesaReceiptNumber":

                        payment.mpesa_receipt_number = (
                            item.get("Value")
                        )

                        break

            else:

                payment.status = "Failed"

            payment.save()

        return JsonResponse(
            {
                "ResultCode": 0,
                "ResultDesc": "Callback received successfully",
            }
        )

    except Exception as error:

        print(
            f"M-Pesa callback error: {error}"
        )

        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Callback processing failed",
            },
            status=500,
        )