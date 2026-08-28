from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import UserStreak, ActivityLog, MoodLog
from community.models import Post, Like, Comment

class ProgressOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        start_of_week = now - timedelta(days=6)

        # 1. Streak Data
        streak, _ = UserStreak.objects.get_or_create(user=user)
        streak_data = {
            "current": streak.current_streak,
            "longest": streak.longest_streak,
            "most_active_time": streak.most_active_time
        }

        # 2. Weekly Activity Data
        weekly_activities = ActivityLog.objects.filter(user=user, created_at__gte=start_of_week)
        calming_count = weekly_activities.filter(activity_type='calming_session').count()
        breathing_count = weekly_activities.filter(activity_type='mindful_breathing').count()
        affirmation_count = weekly_activities.filter(activity_type='affirmation').count()

        weekly_activity_data = {
            "calming_sessions": calming_count,
            "mindful_breathing": breathing_count,
            "affirmations": affirmation_count
        }

        # 3. Community Voice Data
        weekly_posts = Post.objects.filter(user=user, created_at__gte=start_of_week)
        posts_count = weekly_posts.count()
        
        # Calculate total engagement (likes and comments on this user's posts)
        user_posts = Post.objects.filter(user=user)
        total_likes = Like.objects.filter(post__in=user_posts).count()
        total_comments = Comment.objects.filter(post__in=user_posts).count()
        
        community_voice_data = {
            "posts_shared_this_week": posts_count,
            "engagement_received": total_likes + total_comments
        }

        # 4. Mood Insights Data
        # Get mood logs for the last 7 days
        moods = MoodLog.objects.filter(user=user, created_at__gte=start_of_week)
        
        # Calculate most viewed content/mood
        most_frequent_mood = moods.values('mood').annotate(count=Count('mood')).order_by('-count').first()
        most_viewed_content = most_frequent_mood['mood'] if most_frequent_mood else "Confident"

        # Prepare chart data (simple mock aggregation for demonstration)
        # In a real scenario, you group by day of the week
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        chart_data = []
        for i in range(7):
            target_date = start_of_week + timedelta(days=i)
            day_name = days[target_date.weekday()]
            # Just grabbing the first mood of that day for the chart's primary icon, or default to Happy
            day_moods = moods.filter(created_at__date=target_date.date())
            count = day_moods.count()
            primary_mood = day_moods.first().mood if day_moods.exists() else 'Happy'
            
            chart_data.append({
                "day": day_name,
                "mood": primary_mood,
                "count": count
            })

        mood_insights_data = {
            "most_viewed_content": most_viewed_content,
            "chart_data": chart_data
        }

        # Final Response
        return Response({
            "streak": streak_data,
            "weekly_activity": weekly_activity_data,
            "community_voice": community_voice_data,
            "mood_insights": mood_insights_data
        })

class MoodLogCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mood = request.data.get('mood')
        if not mood:
            return Response({"error": "Mood is required"}, status=400)
        
        MoodLog.objects.create(user=request.user, mood=mood)
        return Response({"message": "Mood logged successfully"}, status=201)

class ActivityLogCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        activity_type = request.data.get('activity_type')
        if not activity_type:
            return Response({"error": "Activity type is required"}, status=400)
            
        ActivityLog.objects.create(user=request.user, activity_type=activity_type)
        return Response({"message": "Activity logged successfully"}, status=201)
