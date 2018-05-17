import ast

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
    """
    Types of AHA Group fields
    """
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

    type = models.CharField(_("type"), max_length=64, choices=FIELD_TYPES,
                            default="")
    value = ArrayField(
        models.CharField(_("value"), max_length=128, default=""))
    user = models.ForeignKey('auth_core.User', related_name='aha_fields',
                             verbose_name=_("user"))

    class Meta(object):
        verbose_name = _("aha field")
        verbose_name_plural = _("aha field")

    def __str__(self):
        return "{type}".format(type=self.type)


class EnrollClassTime(TimeStampedModel):
    date = models.CharField(_("date"), max_length=10, default="")
    start = models.CharField(_("start"), max_length=10, default="")
    end = models.CharField(_("end"), max_length=10, default="")
    group_id = models.CharField(_("group id"), max_length=128, default="")

    class Meta(object):
        verbose_name = _("enroll class time")
        verbose_name_plural = _("enroll class times")

    def __str__(self):
        return "{type}".format(type=self.date)


class AHAGroup(models.Model):
    """
    Model of AHA Group received from AHA service
    """

    enrollware_group = models.OneToOneField('EnrollWareGroup',
                                            on_delete=models.CASCADE,
                                            blank=True, null=True,
                                            related_name='aha_group')

    course = models.CharField(_("course"), max_length=128, default="")
    location = models.CharField(_("location"), max_length=128, default="")
    instructor = models.CharField(_("instructor"), max_length=64, default="")
    training_center = models.CharField(_("training center"), max_length=128,
                                       default="")
    training_site = models.CharField(_("training site"), max_length=128,
                                     default="")
    roster_limit = models.IntegerField(_("max students"), default=0)
    cutoff_date = models.CharField(_("cutoff date"), max_length=10, default="")
    description = models.CharField(_("description"), max_length=1024,
                                   default="")
    notes = models.CharField(_("note"), max_length=1024, default="")

    class Meta(object):
        verbose_name = _("aha group")
        verbose_name_plural = _("aha groups")

    def str(self):
        return "{type}".format(type=self.course)

    @staticmethod
    def normalize_value(value):
        return value.strip()

    def get_verbose(self, field):

        str_fields = ['description', 'notes']

        mapper = {
            'course': AHAField.FIELD_TYPES.COURSE,
            'location': AHAField.FIELD_TYPES.LOCATION,
            'training_center': AHAField.FIELD_TYPES.TC,
            'training_site': AHAField.FIELD_TYPES.TS,
            'instructor': AHAField.FIELD_TYPES.INSTRUCTOR,
        }

        value = self.normalize_value(getattr(self, field))

        if field in str_fields:
            return value

        user = self.enrollware_group.user
        try:
            aha_field = AHAField.objects.get(user_id=user.id,
                                             type=mapper[field])
        except AHAField.DoesNotExist:
            return ''

        print("BEFORE: {}".format(aha_field.value))

        for item in aha_field.value:
            print(aha_field.value)
            item = ast.literal_eval(item)
            if item['value'] == value:
                return item['text']


class EnrollWareGroup(TimeStampedModel):
    """
    Instance of EnrollWare Group received from EnrollWare service
    """
    STATUS_CHOICES = Choices(
        ('unsynced', 'UNSYNCED', _("Unsynced")),
        ('synced', 'SYNCED', _("Synced")),
        ('in_progress', 'IN_PROGRESS', _("In progress")),
        ('error', 'ERROR', _("Error"))
    )

    user = models.ForeignKey('auth_core.User',
                             related_name='enrollware_groups',
                             verbose_name=_("user"))
    group_id = models.CharField(_("group id"), max_length=128, default="")
    course = models.CharField(_("course"), max_length=128, default="")
    location = models.CharField(_("location"), max_length=128, default="")
    instructor = models.CharField(_("instructor"), max_length=64, default="")
    max_students = models.IntegerField(_("max students"), default=0)
    status = models.CharField(_("status"), max_length=12,
                              choices=STATUS_CHOICES,
                              default=STATUS_CHOICES.UNSYNCED)
    available_to_export = models.BooleanField(_("available to export"),
                                              default=False)

    sync_date = models.DateTimeField(_("sync date"), null=True)

    class Meta(object):
        verbose_name = _("enroll group")
        verbose_name_plural = _("enroll groups")

    def __str__(self):
        return self.get_course_title()

    @classmethod
    def get_locations(cls):
        """
        Get list of available enrollware locations
        :return: 
        """
        return cls.objects.distinct('location').values_list('location',
                                                            flat=True)

    @classmethod
    def get_courses(cls):
        """
        Get list of available enrollware class types
        :return: 
        """
        return cls.objects.distinct('course').values_list('course',
                                                          flat=True)

    @property
    def class_times(self):
        """
        Mapping class time with EnrollWare Group instance
        """
        return EnrollClassTime.objects.filter(group_id=self.group_id)

    def get_course_title(self):
        return "{}: {}".format(self.course, self.get_class_time_date())

    def get_class_time_date(self):
        class_time = EnrollClassTime.objects.filter(
            group_id=self.group_id).first()
        if class_time is None:
            return ''
        return "{}".format(class_time.date)

    def get_class_time_start(self):
        class_time = EnrollClassTime.objects.filter(
            group_id=self.group_id).first()
        if class_time is None:
            return ''
        return "{}".format(class_time.start)

    def get_class_time_end(self):
        class_time = EnrollClassTime.objects.filter(
            group_id=self.group_id).first()
        if class_time is None:
            return ''
        return "{}".format(class_time.end)

    get_class_time_date.short_description = _('Class Time')

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
    """
    Mapping EnrollWare and AHA values
    """
    aha_field = models.ForeignKey("AHAField", verbose_name=_("aha field"),
                                  on_delete=models.CASCADE)
    enroll_value = models.CharField(_("enroll value"), max_length=128,
                                    default="")
    aha_value = models.CharField(_("aha_value"), max_length=128, default="")
    user = models.ForeignKey("auth_core.User", related_name='mappers',
                             verbose_name=_("user"), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("mapper")
        verbose_name_plural = _("mappers")

    def __str__(self):
        return "{type} {user}".format(type=self.aha_field, user=self.user)


class BaseCredentials(TimeStampedModel):
    username = models.CharField(_("username"), max_length=32, default="")
    password = models.CharField(_("password"), max_length=16, default="")
    user = models.ForeignKey("auth_core.User", related_name='%(class)s',
                             verbose_name=_("user"))

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
