from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def has_services_credentials(self):
        return self.ahacredentials.exists() and self.enrollwarecredentials.exists()
