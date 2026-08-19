import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the production admin from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "")
        if not username and not password:
            self.stdout.write("No admin credentials configured; skipping.")
            return
        if not username or not password:
            raise CommandError("DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD are both required")
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email
        user.is_staff = user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS("Production admin created/updated."))
