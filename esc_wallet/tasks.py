from celery import shared_task
from .walletActions import transferFromTreasury

@shared_task
def initiateTransfer(walletPk, transaction_type, amount=0):
    transferFromTreasury(walletPk, transaction_type, amount)

