import requests

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyAffirmationCache, JournalEntry
from .serializers import JournalEntrySerializer


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

	def get(self, request):
		try:
			# Pass query parameters (like user_id, content_id) directly to the FastAPI server
			payload = proxy_ai_meditation_request('GET', params=request.query_params)
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the AI meditation service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)
		return Response(payload, status=status.HTTP_200_OK)

	def post(self, request):
		# Automatically save the mood for the Progress chart if provided
		mood = request.data.get('mood')
		if mood and request.user.is_authenticated:
			from progress.models import MoodLog
			MoodLog.objects.create(user=request.user, mood=mood)

		try:
			payload = proxy_ai_meditation_request('POST', payload=request.data)
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the AI meditation service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(payload, status=status.HTTP_200_OK)


class JournalView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		question = request.data.get('question')
		prompt = request.data.get('prompt')

		if not question or not prompt:
			return Response(
				{'detail': 'question and prompt are required.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		service_url = getattr(
			settings,
			'JOURNAL_SERVICE_URL',
			'http://187.127.98.88:8050/api/journal',
		)
		timeout = getattr(settings, 'JOURNAL_SERVICE_TIMEOUT', 240)

		try:
			response = requests.post(
				service_url,
				json={'question': question, 'prompt': prompt},
				timeout=timeout,
			)
			response.raise_for_status()
			payload = response.json()
			
			# Save to local database
			user = request.user if request.user.is_authenticated else None
			JournalEntry.objects.create(
				user=user,
				question=question,
				prompt=prompt,
				ai_response=payload
			)
			
		except requests.RequestException as exc:
			return Response(
				{'detail': f'Unable to reach the journal service: {exc}'},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(payload, status=status.HTTP_200_OK)

	def get(self, request):
		if not request.user.is_authenticated:
			return Response(
				{'detail': 'Authentication required to view journal history.'},
				status=status.HTTP_401_UNAUTHORIZED
			)
			
		journals = JournalEntry.objects.filter(user=request.user)
		serializer = JournalEntrySerializer(journals, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
