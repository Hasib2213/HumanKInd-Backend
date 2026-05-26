from datetime import timedelta
from decimal import Decimal
import uuid

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentTransaction, SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class MySubscriptionView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = UserSubscription.objects.get_or_create(user=self.request.user)
        return obj

class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        sub, created = UserSubscription.objects.get_or_create(user=request.user)
        
        # If user is already active on another plan, we might update it
        sub.plan = plan
        if created or sub.status == 'trialing' or not sub.trial_start_date:
            sub.status = 'trialing'
            sub.trial_start_date = timezone.now()
            trial_days = plan.trial_days if hasattr(plan, 'trial_days') else 7
            sub.trial_end_date = sub.trial_start_date + timedelta(days=trial_days)
        else:
            # If trial is already over or they had a previous subscription
            if sub.trial_end_date and timezone.now() > sub.trial_end_date:
                sub.status = 'active'
                sub.current_period_start = timezone.now()
                sub.current_period_end = sub.current_period_start + timedelta(days=plan.duration_days)
            else:
                sub.status = 'trialing'
        
        sub.is_canceled = False
        sub.save()
        
        serializer = UserSubscriptionSerializer(sub)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            sub = UserSubscription.objects.get(user=request.user)
            sub.is_canceled = True
            sub.status = 'canceled'
            sub.save()
            return Response({'message': 'Subscription canceled successfully'}, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response({'error': 'No active subscription found'}, status=status.HTTP_404_NOT_FOUND)


def _generate_transaction_id(user, plan):
    return f"SUB-{user.id}-{plan.id}-{uuid.uuid4().hex[:10].upper()}"


def _get_sslcommerz_urls(request):
    success_url = request.build_absolute_uri(reverse('sslcommerz-success'))
    fail_url = request.build_absolute_uri(reverse('sslcommerz-fail'))
    cancel_url = request.build_absolute_uri(reverse('sslcommerz-cancel'))
    return success_url, fail_url, cancel_url


def _build_gateway_payload(request, transaction):
    success_url, fail_url, cancel_url = _get_sslcommerz_urls(request)
    first_name = getattr(request.user, 'first_name', '') or ''
    last_name = getattr(request.user, 'last_name', '') or ''
    full_name = f'{first_name} {last_name}'.strip() or getattr(request.user, 'email', '') or 'Customer'

    return {
        'store_id': settings.SSL_COMMERZ_STORE_ID,
        'store_passwd': settings.SSL_COMMERZ_STORE_PASS,
        'total_amount': str(transaction.amount),
        'currency': transaction.currency,
        'tran_id': transaction.transaction_id,
        'success_url': success_url,
        'fail_url': fail_url,
        'cancel_url': cancel_url,
        'ipn_url': success_url,
        'cus_name': full_name,
        'cus_email': request.user.email or 'customer@example.com',
        'cus_add1': 'Unknown',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'cus_phone': '00000000000',
        'product_name': transaction.plan.name if transaction.plan else 'Subscription',
        'product_category': 'subscription',
        'product_profile': 'non-physical-goods',
        'shipping_method': 'NO',
        'multi_card_name': 'visa,mastercard,amex,dbbl,other',
    }


def _initiate_sslcommerz_payment(request, plan, subscription):
    if not settings.SSL_COMMERZ_STORE_ID or not settings.SSL_COMMERZ_STORE_PASS:
        return Response(
            {'error': 'SSLCommerz credentials are not configured in the environment.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    transaction = PaymentTransaction.objects.create(
        user=request.user,
        subscription=subscription,
        plan=plan,
        transaction_id=_generate_transaction_id(request.user, plan),
        amount=plan.price,
        currency='BDT',
        status='pending',
    )

    payload = _build_gateway_payload(request, transaction)
    init_url = f"{settings.SSL_COMMERZ_BASE_URL}/gwprocess/v4/api.php"

    try:
        gateway_response = requests.post(init_url, data=payload, timeout=30)
        gateway_response.raise_for_status()
        response_data = gateway_response.json()
    except (requests.RequestException, ValueError) as exc:
        transaction.status = 'failed'
        transaction.gateway_response = {'error': str(exc)}
        transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])
        return Response(
            {'error': 'Unable to initialize SSLCommerz payment.', 'details': str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    transaction.gateway_response = response_data
    transaction.status = 'initiated'
    transaction.gateway_url = response_data.get('GatewayPageURL')
    transaction.save(update_fields=['status', 'gateway_url', 'gateway_response', 'updated_at'])

    if response_data.get('status') != 'SUCCESS' or not transaction.gateway_url:
        transaction.status = 'failed'
        transaction.save(update_fields=['status', 'updated_at'])
        return Response(
            {'error': 'SSLCommerz did not return a gateway URL.', 'response': response_data},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            'message': 'Payment initialized successfully.',
            'transaction_id': transaction.transaction_id,
            'payment_url': transaction.gateway_url,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
        },
        status=status.HTTP_200_OK,
    )


def _validate_sslcommerz_transaction(transaction_id, val_id):
    validation_url = (
        f"{settings.SSL_COMMERZ_BASE_URL}/validator/api/validationserverAPI.php"
        f"?val_id={val_id}&store_id={settings.SSL_COMMERZ_STORE_ID}"
        f"&store_passwd={settings.SSL_COMMERZ_STORE_PASS}&format=json"
    )
    response = requests.get(validation_url, timeout=30)
    response.raise_for_status()
    return response.json()


def _finalize_sslcommerz_payment(request, outcome):
    transaction_id = (
        request.data.get('tran_id')
        or request.POST.get('tran_id')
        or request.query_params.get('tran_id')
        or request.GET.get('tran_id')
    )
    val_id = (
        request.data.get('val_id')
        or request.POST.get('val_id')
        or request.query_params.get('val_id')
        or request.GET.get('val_id')
    )

    if not transaction_id:
        return Response({'error': 'tran_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        transaction = PaymentTransaction.objects.select_related('user', 'plan', 'subscription').get(transaction_id=transaction_id)
    except PaymentTransaction.DoesNotExist:
        return Response({'error': 'Payment transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    if outcome == 'success':
        if not val_id:
            return Response({'error': 'val_id is required for success validation'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validation_data = _validate_sslcommerz_transaction(transaction_id, val_id)
        except (requests.RequestException, ValueError) as exc:
            transaction.status = 'failed'
            transaction.validation_response = {'error': str(exc)}
            transaction.save(update_fields=['status', 'validation_response', 'updated_at'])
            return Response(
                {'error': 'Could not validate payment with SSLCommerz.', 'details': str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        transaction.val_id = val_id
        transaction.validation_response = validation_data

        validation_status = str(validation_data.get('status', '')).upper()
        if validation_status not in {'VALID', 'VALIDATED'}:
            transaction.status = 'failed'
            transaction.save(update_fields=['status', 'val_id', 'validation_response', 'updated_at'])
            return Response(
                {'error': 'SSLCommerz validation failed.', 'response': validation_data},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_transaction_id = validation_data.get('tran_id')
        validated_amount = validation_data.get('amount')
        if validated_transaction_id and str(validated_transaction_id) != str(transaction_id):
            transaction.status = 'failed'
            transaction.save(update_fields=['status', 'val_id', 'validation_response', 'updated_at'])
            return Response(
                {'error': 'Transaction id mismatch during validation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if validated_amount is not None and Decimal(str(validated_amount)) != Decimal(str(transaction.amount)):
            transaction.status = 'failed'
            transaction.save(update_fields=['status', 'val_id', 'validation_response', 'updated_at'])
            return Response(
                {'error': 'Amount mismatch during validation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription, _ = UserSubscription.objects.get_or_create(user=transaction.user)
        subscription.plan = transaction.plan
        subscription.status = 'active'
        subscription.is_canceled = False
        subscription.trial_start_date = None
        subscription.trial_end_date = None
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = subscription.current_period_start + timedelta(days=transaction.plan.duration_days)
        subscription.save()

        transaction.subscription = subscription
        transaction.status = 'success'
        transaction.save(update_fields=['subscription', 'status', 'val_id', 'validation_response', 'updated_at'])

        return Response(
            {
                'message': 'Payment verified and subscription activated.',
                'transaction_id': transaction.transaction_id,
                'subscription_id': str(subscription.id),
                'status': subscription.status,
            },
            status=status.HTTP_200_OK,
        )

    transaction.status = 'canceled' if outcome == 'cancel' else 'failed'
    transaction.val_id = val_id or transaction.val_id
    transaction.save(update_fields=['status', 'val_id', 'updated_at'])
    return Response(
        {'message': f'Payment {outcome}.', 'transaction_id': transaction.transaction_id},
        status=status.HTTP_200_OK,
    )


class SSLCommerzInitiateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        subscription = UserSubscription.objects.filter(user=request.user).first()
        return _initiate_sslcommerz_payment(request, plan, subscription)


class SSLCommerzSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return _finalize_sslcommerz_payment(request, 'success')

    def get(self, request):
        return _finalize_sslcommerz_payment(request, 'success')


class SSLCommerzFailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return _finalize_sslcommerz_payment(request, 'fail')

    def get(self, request):
        return _finalize_sslcommerz_payment(request, 'fail')


class SSLCommerzCancelView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return _finalize_sslcommerz_payment(request, 'cancel')

    def get(self, request):
        return _finalize_sslcommerz_payment(request, 'cancel')
