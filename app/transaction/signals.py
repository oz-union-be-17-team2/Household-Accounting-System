from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Transaction


@receiver(pre_save, sender=Transaction)
def revert_account_balance_on_update(sender, instance, **kwargs):
    if not instance._state.adding:
        old = Transaction.objects.get(pk=instance.pk)
        account = old.account
        if old.transaction_type == Transaction.TransactionType.DEPOSIT:
            account.balance -= old.amount
        elif old.transaction_type == Transaction.TransactionType.WITHDRAWAL:
            account.balance += old.amount
        if instance.transaction_type == Transaction.TransactionType.DEPOSIT:
            account.balance += instance.amount
        elif instance.transaction_type == Transaction.TransactionType.WITHDRAWAL:
            account.balance -= instance.amount
        account.save()


@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        if instance.transaction_type == Transaction.TransactionType.DEPOSIT:
            account.balance += instance.amount
        elif instance.transaction_type == Transaction.TransactionType.WITHDRAWAL:
            account.balance -= instance.amount
        account.save()


@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    account = instance.account
    if instance.transaction_type == Transaction.TransactionType.DEPOSIT:
        account.balance -= instance.amount
    elif instance.transaction_type == Transaction.TransactionType.WITHDRAWAL:
        account.balance += instance.amount
    account.save()
