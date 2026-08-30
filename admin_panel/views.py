from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from Authapp.serializers import UserSerializer
from subscriptions.models import UserSubscription
from community.models import Post
from progress.models import ActivityLog

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_posts = Post.objects.count()
        total_sessions = ActivityLog.objects.count()
        
        # Calculate active subscriptions
        active_subs = UserSubscription.objects.filter(status='active')
        
        # Free vs Annual vs Monthly (approximate based on active subs)
        annual_users = active_subs.filter(plan__name__icontains='annual').count()
        monthly_users = active_subs.filter(plan__name__icontains='monthly').count()
        free_users = total_users - (annual_users + monthly_users)

        return Response({
            "total_users": total_users,
            "inspections_completed": 0, # Placeholder if needed
            "total_sessions_usage": total_sessions,
            "community_posts": total_posts,
            "user_breakdown": {
                "free_users": free_users,
                "annual_users": annual_users,
                "monthly_users": monthly_users
            }
        })

class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        # Here we could implement pagination, but returning all for now
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            
            # Fetch user's subscription
            subs = UserSubscription.objects.filter(user=user).order_by('-created_at')
            sub_history = []
            for sub in subs:
                try:
                    plan_name = sub.plan.name if sub.plan else "Trial"
                except Exception:
                    # In case the referenced SubscriptionPlan was deleted from the DB
                    plan_name = "Trial (Plan Deleted)"

                sub_history.append({
                    "plan": plan_name,
                    "status": "Active" if sub.status == 'active' else "Expired",
                    "start_date": sub.current_period_start,
                    "end_date": sub.current_period_end
                })

            return Response({
                "user": serializer.data,
                "subscription_history": sub_history,
                "longest_streak": 0, # Can join with UserStreak
                "community_posts": Post.objects.filter(user=user).count()
            })
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class UserSuspendView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            # Toggle suspension
            user.is_suspended = not user.is_suspended
            user.suspension_reason = request.data.get('reason', '') if user.is_suspended else ''
            user.save()
            
            status_text = "suspended" if user.is_suspended else "reactivated"
            return Response({"message": f"User {status_text} successfully", "is_suspended": user.is_suspended})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# ----------------- PHASE 3: SUBSCRIPTION MANAGEMENT -----------------

from subscriptions.models import SubscriptionPlan

class AdminSubscriptionPlanUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        try:
            plan = SubscriptionPlan.objects.get(id=pk)
            plan.price = request.data.get('price', plan.price)
            plan.trial_days = request.data.get('trial_days', plan.trial_days)
            plan.most_popular = request.data.get('most_popular', plan.most_popular)
            
            # If this is marked most popular, unmark others
            if plan.most_popular:
                SubscriptionPlan.objects.exclude(id=pk).update(most_popular=False)
                
            plan.save()
            return Response({"message": "Subscription plan updated successfully."})
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

# ----------------- PHASE 4: ADMIN SETTINGS -----------------

class AdminSuspendedUsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_suspended=True)
        serializer = UserSerializer(users, many=True)
        # Adding suspension reason to the response
        data = []
        for user in users:
            d = UserSerializer(user).data
            d['suspension_reason'] = user.suspension_reason
            data.append(d)
        return Response(data)

class AdminManagementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admins = User.objects.filter(is_staff=True)
        serializer = UserSerializer(admins, many=True)
        return Response(serializer.data)

    def post(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        admin_user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name="Admin"
        )
        return Response({"message": "Admin created successfully.", "user_id": str(admin_user.id)})

class AdminRemoveView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        if str(request.user.id) == str(pk):
            return Response({"error": "You cannot remove yourself"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin_user = User.objects.get(id=pk, is_staff=True)
            admin_user.is_staff = False
            admin_user.is_superuser = False
            admin_user.save()
            return Response({"message": "Admin privileges removed successfully."})
        except User.DoesNotExist:
            return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

# ----------------- PHASE 5: PLATFORM SETTING -----------------

from .models import PlatformSetting
from .serializers import PlatformSettingSerializer

class AdminPlatformSettingView(APIView):
    permission_classes = [IsAdminUser]

    def get_setting(self):
        setting = PlatformSetting.objects.first()
        if not setting:
            setting = PlatformSetting.objects.create()
        return setting

    def get(self, request):
        setting = self.get_setting()
        serializer = PlatformSettingSerializer(setting)
        return Response(serializer.data)

    def put(self, request):
        setting = self.get_setting()
        serializer = PlatformSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Platform settings updated successfully.", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicPlatformSettingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        setting = PlatformSetting.objects.first()
        if not setting:
            setting = PlatformSetting.objects.create()
        serializer = PlatformSettingSerializer(setting)
        return Response(serializer.data)

# ----------------- PHASE 2: COMMUNITY MODERATION -----------------

class AdminCommunityPostListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        posts = Post.objects.annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            reports_count=Count('reports', distinct=True)
        ).order_by('-created_at')

        data = []
        for p in posts:
            data.append({
                "id": str(p.id),
                "user": UserSerializer(p.user).data,
                "content": p.content,
                "created_at": p.created_at,
                "likes_count": p.likes_count,
                "comments_count": p.comments_count,
                "reports_count": p.reports_count,
            })
        
        return Response(data)

class AdminCommunityPostDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            likes = post.likes.all()
            comments = post.comments.all()
            reports = post.reports.all()

            return Response({
                "post_id": str(post.id),
                "content": post.content,
                "user": UserSerializer(post.user).data,
                "liked_by": [{"user_id": str(l.user.id), "email": l.user.email, "name": l.user.first_name} for l in likes],
                "commented_by": [{"user_id": str(c.user.id), "email": c.user.email, "comment": c.content} for c in comments],
                "reported_by": [{"user_id": str(r.user.id), "email": r.user.email, "title": r.title, "description": r.description} for r in reports],
            })
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

from notifications.models import Notification

class AdminUserWarnView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            message = request.data.get('message', 'This is a warning from the community guidelines team.')
            
            # Send Notification
            Notification.objects.create(
                user=user,
                title="Community Guidelines Warning",
                message=message,
                notification_type="alert"
            )
            
            return Response({"message": f"Warning sent to {user.email} successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
