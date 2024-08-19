from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Balance, CustomUser


@receiver(post_save, sender=CustomUser)
def create_user_balance(sender, instance: CustomUser, created, **kwargs):
    """
    При создании объекта в модели CustomUser
    будет автоматически создаваться связанный объект в модели Balance
    """

    if created:
        Balance.objects.create(user=instance)
