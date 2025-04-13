from celery import shared_task
from time import sleep
from .hubFinder import findHub
from .getCoordinates import map_number

@shared_task
def hubFindingTask(orderId):
    findHub(orderId)
    
    
@shared_task
def mapNumberTask(addressPk):
    map_number(addressPk)