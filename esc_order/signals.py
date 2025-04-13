from django.dispatch import Signal, receiver
from .tasks import hubFindingTask
from .tasks import mapNumberTask

order_creation_signal = Signal()
map_number_signal = Signal()


@receiver(order_creation_signal)
def handleHubFinding(sender, orderId, **kwargs):
    hubFindingTask.delay(orderId)
    
@receiver(map_number_signal)
def handleMapNumber(sender, addressPk, **kwargs):
    mapNumberTask.delay(addressPk)
