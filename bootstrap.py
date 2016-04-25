from celery.utils.log import get_task_logger
from celery import Celery
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from Publisher import Publisher

routing_key = 'ped_routing_key'
queue_name = 'pedQueue'
exchange_name = 'pedQueueEx'
my_queue = Queue(queue_name, Exchange(exchange_name), routing_key)

app = Celery(broker='amqp://')

logger = get_task_logger(__name__)


class MyConsumerStep(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[my_queue],
                         callbacks=[self.handle_message],
                         accept=['json'])]

    def handle_message(self, body, message):
        print('Received message: {0!r}'.format(body))
        message.ack()
app.steps['consumer'].add(MyConsumerStep)


def send_me_a_message(self):
    message = {"short_code": 26577,
            "msisdn": 254711442224,
            "message": "Test Message here",
            "network": "SAFARICOM",
            "sdp_id": 6013842000001443,
            "alert_type": "BULK",
            "correlator": 63637378,
            "linkId": None}
    pyb = Publisher(queue_name, exchange_name, logger)
    inject = pyb.publish(message, routing_key)
    logger.info("inject result {0!r}".format(inject))

if __name__ == '__main__':
    send_me_a_message('celery')