from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _

AHA_OCCURRENCE_CHOICES = (
    ('SN', 'Single'),
    ('WK', 'Weekly'),
    ('MN', 'Monthly')
)


class AHAField(models.Model):
    type = models.CharField(_("type"), max_length=64, default="")
    value = ArrayField(models.CharField(_("value"), max_length=128, default=""))

    class Meta(object):
        verbose_name = _("aha field")
        verbose_name_plural = _("aha field")

    #TODO: def get_default_value()

    def __str__(self):
        return "{type}".format(type=self.type)


class EnrollClassTime(models.Model):
    date = models.DateField(_("date"))
    start = models.TimeField(_("start"))
    end = models.TimeField(_("end"))
    group = models.ForeignKey("EnrollWareGroup", verbose_name=_("group"), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("enroll class time")
        verbose_name_plural = _("enroll class times")

    def __str__(self):
        return "{type}".format(type=self.date)


class AHAClassSchedule(models.Model):
    class_description = models.CharField(_("class description"), max_length=256, default="")
    occurrence = models.CharField(_("occurrence"), max_length=2, choices=AHA_OCCURRENCE_CHOICES, default="SN")
    date = models.DateField(_("date"))
    start = models.TimeField(_("start"))
    end = models.TimeField(_("end"))
    group = models.ForeignKey("AHAGroup", verbose_name=_("group"), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("aha class schedule")
        verbose_name_plural = _("aha class schedules")

    def __str__(self):
        return "{type}".format(type=self.date)


class EnrollWareGroup(models.Model):
    group_id = models.IntegerField(_("group id"))
    course = models.CharField(_("course"), max_length=128, default="")
    location = models.CharField(_("location"), max_length=128, default="")
    instructor = models.CharField(_("instructor"), max_length=64, default="")
    max_students = models.IntegerField(_("max students"), default=0)
    synced = models.BooleanField(_("synced"), default=False)

    class Meta(object):
        verbose_name = _("enroll group")
        verbose_name_plural = _("enroll groups")

    def __str__(self):
        return "{type}".format(type=self.course)


#TODO: We have no group_id at group creating
class AHAGroup(models.Model):
    course = models.CharField(_("course"), max_length=128, default="")
    location = models.CharField(_("location"), max_length=128, default="")
    instructor = models.CharField(_("instructor"), max_length=64, default="")
    training_center = models.CharField(_("training center"), max_length=128, default="")
    training_site = models.CharField(_("training site"), max_length=128, default="")
    roster_limit = models.IntegerField(_("max students"), default=0)

    class Meta(object):
        verbose_name = _("aha group")
        verbose_name_plural = _("aha groups")

    def __str__(self):
        return "{type}".format(type=self.course)


class Mapper(models.Model):
    aha_field = models.ForeignKey("AHAField", verbose_name=_("aha field"), on_delete=models.CASCADE)
    enroll_value = models.CharField(_("enroll value"), max_length=128, default="")
    aha_value = models.CharField(_("aha_value"), max_length=128, default="")
    user = models.ForeignKey("auth.User", verbose_name=_("user"), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("mapper")
        verbose_name_plural = _("mappers")

    def __str__(self):
        return "{type}".format(type=self.aha_field)








