from celery.utils.log import get_task_logger
from celery import Celery
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from Publisher import Publisher
from utils import LocalConfigParser


rabbit_configs = LocalConfigParser.parse_configs("RABBIT")
sdp_configs = LocalConfigParser.parse_configs("SDP")
print "CONFILS", rabbit_configs

host = rabbit_configs['rabbithost']
username = rabbit_configs['rabbitusername']
password = rabbit_configs['rabbitpassword']
port = rabbit_configs['rabbitport']
vhost = rabbit_configs['rabbitvhost']
sdp_url = sdp_configs["url"]
bulk_url = sdp_configs["bulk_url"]

routing_key = 'ped_routing_key'
queue_name = 'pedQueue'
exchange_name = 'pedQueueEx'
my_queue = Queue(queue_name, Exchange(exchange_name, type='fanout'), routing_key)

BROKER_URL = 'amqp://{user}:{password}@{host}:{port}//'.format(
    user=username,
    password=password,
    host=host,
    port=port
)
app = Celery(broker=BROKER_URL)

logger = get_task_logger(__name__)


class MyConsumerStep(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[my_queue],
                         callbacks=[self.on_message])]

    def on_message(self, body, message):
        logger.info("GOT MESSAGE body:: %r " % body)
        message.ack()

app.steps['consumer'].add(MyConsumerStep)


class ProducerStep(bootsteps.Step):

    def __init__(self, parent, **kwargs):
        # here we can prepare the Worker/Consumer object
        # in any way we want, set attribute defaults and so on.
        self.send_me_a_message()
        logger.info('{0!r} is in init'.format(parent))

    def start(self, parent):
        # our step is started together with all other Worker/Consumer
        # bootsteps.
        logger.info('{0!r} is starting'.format(parent))

    def stop(self, parent):
        # the Consumer calls stop every time the consumer is restarted
        # (i.e. connection is lost) and also at shutdown.  The Worker
        # will call stop at shutdown only.
        logger.info('{0!r} is stopping'.format(parent))

    def shutdown(self, parent):
        # shutdown is called by the Consumer at shutdown, it's not
        # called by Worker.
        logger.info('{0!r} is shutting down'.format(parent))

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

app.steps['worker'].add(ProducerStep)