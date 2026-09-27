import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the production admin account."

    def handle(self, *args, **options):

        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not password:
            raise CommandError(
                "ADMIN_USERNAME and ADMIN_PASSWORD must be set."
            )

        user, created = User.objects.get_or_create(
            username=username
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.set_password(password)

        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin account '{username}' created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin account '{username}' updated successfully."
                )
            )