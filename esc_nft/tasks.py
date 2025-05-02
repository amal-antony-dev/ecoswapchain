from celery import shared_task
from . import mintNFT
from . import sus_predict

@shared_task
def nftTransferTask(orderId, tx_hash):
    mintNFT.transfer(orderId, tx_hash)
    
    
@shared_task
def susScoreTask(nftId):
    sus_predict.predict(nftId)
    
