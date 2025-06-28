from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from django.conf import settings
import uuid

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        booking_ref = data.get("booking_reference")
        amount = data.get("amount")
        email = data.get("email")

        tx_ref = str(uuid.uuid4())  # Unique transaction reference

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "tx_ref": tx_ref,
            "callback_url": "http://yourdomain.com/verify-payment/",
            "return_url": "http://yourdomain.com/payment-success/",
            "customization": {
                "title": "Travel Booking",
                "description": "Pay for your booking"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)

        if response.status_code == 200:
            res_data = response.json()
            Payment.objects.create(
                booking_reference=booking_ref,
                amount=amount,
                transaction_id=tx_ref,
                status='Pending'
            )
            return JsonResponse({"checkout_url": res_data['data']['checkout_url']})
        else:
            return JsonResponse({"error": "Failed to initiate payment"}, status=400)



@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        tx_ref = data.get("tx_ref")

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)

        if response.status_code == 200:
            res_data = response.json()
            status = res_data['data']['status']

            payment = Payment.objects.get(transaction_id=tx_ref)
            if status == "success":
                payment.status = "Completed"
            else:
                payment.status = "Failed"
            payment.save()

            return JsonResponse({"status": payment.status})
        else:
            return JsonResponse({"error": "Failed to verify payment"}, status=400)

