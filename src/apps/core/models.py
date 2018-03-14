from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from django.dispatch import receiver
from django.db.models.signals import post_delete
from model_utils import Choices

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices

AHA_OCCURRENCE_CHOICES = (
    ('SN', 'Single'),
    ('WK', 'Weekly'),
    ('MN', 'Monthly')
)


class AHAField(TimeStampedModel):

    FIELD_TYPES = Choices(
        ('course', 'COURSE', _("Course")),
        ('location', 'LOCATION', _("Location")),
        ('instructor', 'INSTRUCTOR', _("Instructor")),
        ('tc', 'TC', _("Training Center")),
        ('ts', 'TS', _("Training Site")),
        ('lang', 'LANGUAGE', _("Language")),
        ('class_description', 'CLASS_DESCRIPTION', _("Class description")),
        ('class_notes', 'CLASS_NOTES', _("Class notes"))

    )

    type = models.CharField(_("type"), max_length=64, choices=FIELD_TYPES, default="")
    value = ArrayField(models.CharField(_("value"), max_length=128, default=""))
    user = models.ForeignKey('auth_core.User', related_name='aha_fields', verbose_name=_("user"))

    class Meta(object):
        verbose_name = _("aha field")
        verbose_name_plural = _("aha field")

    def __str__(self):
        return "{type}".format(type=self.type)


class EnrollClassTime(TimeStampedModel):
    date = models.CharField(_("date"), max_length=10, default="")
    start = models.CharField(_("start"), max_length=10, default="")
    end = models.CharField(_("end"), max_length=10, default="")
    group_id = models.IntegerField(_("group id"))

    class Meta(object):
        verbose_name = _("enroll class time")
        verbose_name_plural = _("enroll class times")

    def __str__(self):
        return "{type}".format(type=self.date)


class EnrollWareGroup(TimeStampedModel):

    STATUS_CHOICES = Choices(
        ('unsynced', 'UNSYNCED', _("Unsynced")),
        ('synced', 'SYNCED', _("Synced")),
        ('in_progress', 'IN_PROGRESS', _("In progress")),
        ('error', 'ERROR', _("Error"))
    )

    user = models.ForeignKey('auth_core.User', related_name='enrollware_groups', verbose_name=_("user"))
    group_id = models.IntegerField(_("group id"))
    course = models.CharField(_("course"), max_length=128, default="")
    location = models.CharField(_("location"), max_length=128, default="")
    instructor = models.CharField(_("instructor"), max_length=64, default="")
    max_students = models.IntegerField(_("max students"), default=0)
    status = models.CharField(_("status"), max_length=12, choices=STATUS_CHOICES, default=STATUS_CHOICES.UNSYNCED)
    available_to_export = models.BooleanField(_("available to export"), default=False)

    class Meta(object):
        verbose_name = _("enroll group")
        verbose_name_plural = _("enroll groups")

    def __str__(self):
        return "{type}".format(type=self.course)

    @property
    def class_times(self):
        return EnrollClassTime.objects.filter(group_id=self.group_id)

    def get_cutoff_date(self):
        obj = self.class_times.first()
        if obj is None:
            return None
        class_time = "{} {}".format(obj.date, obj.start)
        datetime_object = datetime.strptime(class_time, '%m/%d/%Y %I:%M %p')
        day_before = datetime_object - timedelta(days=1)
        return datetime.strftime(day_before, '%m/%d/%Y')

    def get_default_course(self):
        mapper = Mapper.objects.filter(
            aha_field__type=AHAField.FIELD_TYPES.COURSE,
            user=self.user,
            enroll_value=self.course).last()
        return mapper.aha_value if mapper else None

    def get_default_location(self):
        mapper = Mapper.objects.filter(
            aha_field__type=AHAField.FIELD_TYPES.LOCATION,
            user=self.user,
            enroll_value=self.location).last()
        return mapper.aha_value if mapper else None

    def get_default_instructor(self):
        mapper = Mapper.objects.filter(
            aha_field__type=AHAField.FIELD_TYPES.INSTRUCTOR,
            user=self.user,
            enroll_value=self.instructor).last()
        return mapper.aha_value if mapper else None

    def get_default_description(self):
        mapper = Mapper.objects.filter(
            aha_field__type=AHAField.FIELD_TYPES.CLASS_DESCRIPTION,
            user=self.user,
            enroll_value=self.course).last()
        return mapper.aha_value if mapper else ""

    def get_default_notes(self):
        mapper = Mapper.objects.filter(
            aha_field__type=AHAField.FIELD_TYPES.CLASS_NOTES,
            user=self.user,
            enroll_value=self.course).last()
        return mapper.aha_value if mapper else ""


@receiver(post_delete, sender=EnrollWareGroup)
def delete_times(sender, instance, using, **kwargs):
    EnrollClassTime.objects.filter(group_id=instance.group_id).delete()


class Mapper(TimeStampedModel):
    aha_field = models.ForeignKey("AHAField", verbose_name=_("aha field"), on_delete=models.CASCADE)
    enroll_value = models.CharField(_("enroll value"), max_length=128, default="")
    aha_value = models.CharField(_("aha_value"), max_length=128, default="")
    user = models.ForeignKey("auth_core.User",  related_name='mappers', verbose_name=_("user"), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("mapper")
        verbose_name_plural = _("mappers")

    def __str__(self):
        return "{type} {user}".format(type=self.aha_field, user=self.user)


class BaseCredentials(TimeStampedModel):
    username = models.CharField(_("username"), max_length=32, default="")
    password = models.CharField(_("password"), max_length=16, default="")
    user = models.ForeignKey("auth_core.User", related_name='%(class)s', verbose_name=_("user"))

    class Meta:
        abstract = True


class AHACredentials(BaseCredentials):

    class Meta:
        verbose_name = _("aha credential")
        verbose_name_plural = _("aha credentials")


class EnrollWareCredentials(BaseCredentials):

    class Meta:
        verbose_name = _("enroll credential")
        verbose_name_plural = _("enroll credentials")

