from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from apps.core.models import EnrollWareGroup


class User(AbstractUser):
    """
    User for authorization in the application
    """
    VERSIONS = Choices(
        ('lite', 'LITE', _("Lite")),
        ('pro', 'PRO', _("Pro"))
    )

    version = models.CharField(choices=VERSIONS,
                               default=VERSIONS.LITE, max_length=8,
                               help_text=_("Users with Lite plan could sync one class only"),
                               verbose_name=_("plan"))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__old_version = self.version

    def save(self, *args, **kwargs):
        if self.version != self.__old_version:
            self.set_available_to_export_groups(force=True)
        super(User, self).save(*args, **kwargs)

    def has_services_credentials(self):
        return self.has_enroll_credentials() and self.has_aha_credentials()

    def has_enroll_credentials(self):
        return self.enrollwarecredentials.exists()

    def has_aha_credentials(self):
        return self.ahacredentials.exists()

    def set_available_to_export_groups(self, force=False):
        not_synced_q = ~Q(status=EnrollWareGroup.STATUS_CHOICES.SYNCED)

        if not force and self.version == self.VERSIONS.LITE:
            has_available_to_export_group = self.enrollware_groups.filter(
                available_to_export=True).exists()

            if not has_available_to_export_group:
                try:
                    last_group = self.enrollware_groups.filter(
                        not_synced_q).latest('created')
                except:
                    return None

                last_group.available_to_export = True
                last_group.save()

        if force:
            # if version == lite, set only one group available to export
            if self.version == self.VERSIONS.LITE:
                try:
                    last_group = self.enrollware_groups.filter(
                        not_synced_q).latest('created')
                except:
                    return None

                last_group.available_to_export = True
                last_group.save()

                try:
                    self.enrollware_groups.exclude(id=last_group.id).update(
                        available_to_export=False)
                except:
                    return None

            if self.version == self.VERSIONS.PRO:
                self.enrollware_groups.update(available_to_export=True)

    def get_full_name(self):
        full_name = "{} {}".format(self.first_name, self.last_name).strip()
        return full_name or self.username

    def __str__(self):
        return self.get_full_name()

