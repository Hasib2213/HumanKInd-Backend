from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import UserSubscription
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Checks for subscriptions whose trials will end in exactly 2 days and creates in-app notifications'

    def handle(self, *args, **options):
        # Calculate the date exactly 2 days from now
        target_date = (timezone.now() + timedelta(days=2)).date()
        self.stdout.write(f"Scanning for trial expirations on: {target_date}")

        # Fetch subscriptions that are trialing and end on target_date
        expiring_subscriptions = UserSubscription.objects.filter(
            status='trialing',
            trial_end_date__date=target_date
        )

        created_count = 0
        for sub in expiring_subscriptions:
            if not sub.user:
                continue

            # Prevent duplicate notification for the same target
            title = "Subscription Trial Ending Soon"
            message = f"Your trial for plan '{sub.plan.name if sub.plan else 'mindfulness plan'}' will end in 2 days (on {sub.trial_end_date.strftime('%Y-%m-%d')}). Subscribe to a premium tier to keep unlimited access."
            
            # Check if alert already sent today to avoid double triggers
            already_notified = Notification.objects.filter(
                user=sub.user,
                title=title,
                created_at__date=timezone.now().date()
            ).exists()

            if not already_notified:
                Notification.objects.create(
                    user=sub.user,
                    title=title,
                    message=message,
                    notification_type='subscription'
                )
                self.stdout.write(self.style.SUCCESS(f"Notification created for {sub.user.email}"))
                created_count += 1
            else:
                self.stdout.write(f"User {sub.user.email} already notified today. Skipping.")

        self.stdout.write(self.style.SUCCESS(f"Finished. Created {created_count} notifications."))
