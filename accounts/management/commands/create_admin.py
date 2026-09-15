from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the production admin"

    def handle(self, *args, **options):
        User = get_user_model()

        username = "admin"
        email = "admin@mtech.com"
        password = "7173"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Admin user created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS("Admin password updated successfully."))