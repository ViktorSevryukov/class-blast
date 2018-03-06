from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import ugettext_lazy as _

from model_utils import Choices


class User(AbstractUser):
    VERSIONS = Choices(
        ('lite', 'LITE', _("Lite")),
        ('pro', 'PRO', _("Pro"))
    )

    version = models.CharField(choices=VERSIONS,
                               default=VERSIONS.LITE, max_length=8)

    def has_services_credentials(self):
        return self.ahacredentials.exists() and self.enrollwarecredentials.exists()

    def set_available_to_export_groups(self):

        # if version == lite, set only one group available to export
        if self.version == self.VERSIONS.LITE:
            has_available_to_export_group = self.enrollware_groups.filter(
                available_to_export=True).exists()

            if not has_available_to_export_group:
                try:
                    last_group = self.enrollware_groups.latest('created')
                    last_group.available_to_export = True
                    last_group.save()
                except:
                    pass

        if self.version == self.VERSIONS.PRO:
            #TODO: remove try ?
            try:
                self.enrollware_groups.update(available_to_export=True)
            except:
                pass
