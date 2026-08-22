from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials


class NotificationsConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'notifications'

    def ready(self):
        import os
        from django.conf import settings
        
        # Initialize Firebase when Django starts (if not already initialized)
        if not firebase_admin._apps:
            cred_path = os.path.join(settings.BASE_DIR, 'firebase-adminsdk.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                print(f"Warning: Firebase credential file not found at {cred_path}")
