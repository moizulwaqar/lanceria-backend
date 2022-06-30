from django.db import models
from datetime import datetime
from django.db.models import QuerySet


class ParanoidQuerySet(QuerySet):
    """
    Prevents objects from being hard-deleted. Instead, sets the
    ``date_deleted``, effectively soft-deleting the object.
    """

    # def delete(self):
    #     for obj in self:
    #         obj.deleted_on = datetime.now()
    #         obj.save()


class ParanoidManager(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """

    def get_queryset(self):
        return ParanoidQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=True)


class SoftDeleteModel(models.Model):
    class Meta:
        abstract = True

    deleted_on = models.DateTimeField(null=True, blank=True)
    objects = ParanoidManager()
    original_objects = models.Manager()

    # def delete(self):
    #     self.deleted_on = datetime.now()
    #     self.save()
