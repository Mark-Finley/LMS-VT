import uuid
from django.db import models
from django.conf import settings

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True)

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
    )
    
    status = models.CharField(max_length=50, default='active')
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class NotificationLog(BaseModel):
    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'
    TYPE_WHATSAPP = 'whatsapp'
    TYPE_IN_APP = 'in_app'
    TYPE_CHOICES = [
        (TYPE_EMAIL, 'Email Alert'),
        (TYPE_SMS, 'SMS Text'),
        (TYPE_WHATSAPP, 'WhatsApp Message'),
        (TYPE_IN_APP, 'In-App Notification'),
    ]

    recipient_name = models.CharField(max_length=150)
    recipient_contact = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    is_sent = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient_name} - Sent at {self.sent_at}"

