import requests

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyAffirmationCache


def fetch_daily_affirmation_from_service():
	service_url = getattr(
		settings,
		'DAILY_AFFIRMATION_SERVICE_URL',
		'http://187.127.98.88:8050/api/daily_affirmation',
	)
	timeout = getattr(settings, 'DAILY_AFFIRMATION_SERVICE_TIMEOUT', 20)

	response = requests.post(service_url, timeout=timeout)
	response.raise_for_status()

	payload = response.json()
	affirmation_text = payload.get('affirmation_text')
	voice = payload.get('voice', '')

	if not affirmation_text:
		raise ValueError('FastAPI service returned an invalid affirmation payload.')

	return {
		'affirmation_text': affirmation_text,
		'voice': voice or '',
		'source_payload': payload,
	}


class DailyAffirmationView(APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		today = timezone.localdate()
		cached = DailyAffirmationCache.objects.filter(cache_date=today).first()

		if cached:
			return Response({
				'date': cached.cache_date,
				'affirmation_text': cached.affirmation_text,
				'voice': cached.voice,
				'cached': True,
			}, status=status.HTTP_200_OK)

		try:
			payload = fetch_daily_affirmation_from_service()
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the daily affirmation service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)
		except (ValueError, TypeError) as exc:
			return Response(
				{'detail': str(exc)},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		try:
			with transaction.atomic():
				cached = DailyAffirmationCache.objects.create(
					cache_date=today,
					affirmation_text=payload['affirmation_text'],
					voice=payload['voice'],
					source_payload=payload['source_payload'],
				)
		except IntegrityError:
			cached = DailyAffirmationCache.objects.get(cache_date=today)

		return Response({
			'date': cached.cache_date,
			'affirmation_text': cached.affirmation_text,
			'voice': cached.voice,
			'cached': False,
		}, status=status.HTTP_200_OK)

	def post(self, request):
		return self.get(request)


def proxy_ai_meditation_request(method, payload=None, params=None):
	service_url = getattr(
		settings,
		'AI_MEDITATION_SERVICE_URL',
		'http://187.127.98.88:8050/api/AI_Meditation',
	)
	timeout = getattr(settings, 'AI_MEDITATION_SERVICE_TIMEOUT', 20)

	response = requests.request(
		method=method,
		url=service_url,
		json=payload,
		params=params,
		timeout=timeout,
	)
	response.raise_for_status()
	return response.json()


class AIMeditationView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		try:
			payload = proxy_ai_meditation_request('POST', payload=request.data)
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the AI meditation service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(payload, status=status.HTTP_200_OK)

	def get(self, request):
		user_id = request.query_params.get('user_id')
		content_id = request.query_params.get('content_id')

		if not user_id or not content_id:
			return Response(
				{'detail': 'user_id and content_id are required.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			payload = proxy_ai_meditation_request('GET', params={'user_id': user_id, 'content_id': content_id})
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the AI meditation service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(payload, status=status.HTTP_200_OK)
