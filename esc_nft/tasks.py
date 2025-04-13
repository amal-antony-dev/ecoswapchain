from celery import shared_task
from . import mintNFT

@shared_task
def nftTransferTask(orderId, tx_hash):
    mintNFT.transfer(orderId, tx_hash)
    