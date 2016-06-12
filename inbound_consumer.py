from celery.utils.log import get_task_logger
from celery import Celery
from celery import bootsteps
from kombu import Consumer, Queue
from utils import LocalConfigParser
from Db import Db
import json

rabbit_configs = LocalConfigParser.parse_configs("RABBIT")
sdp_configs = LocalConfigParser.parse_configs("SDP")
print "CONFIGS", rabbit_configs

host = rabbit_configs['rabbithost']
username = rabbit_configs['rabbitusername']
password = rabbit_configs['rabbitpassword']
port = rabbit_configs['rabbitport']
vhost = rabbit_configs['rabbitvhost']
sdp_url = sdp_configs["url"]
bulk_url = sdp_configs["bulk_url"]

BROKER_URL = 'amqp://{user}:{password}@{host}:{port}//'.format(
    user=username,
    password=password,
    host=host,
    port=port
)
app = Celery('inbound_consumer', broker=BROKER_URL)

logger = get_task_logger(__name__)

queue_list = ['BulkStopQueue', 'DLRMNOQUEUE', 'NotifyMNOQUEUE', 'SyncMNOQUEUE']


class AlertConsumerStep(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        consumers = []
        for q in queue_list:
            queue = Queue(q, routing_key=q)
            consumers.append(Consumer(channel, queues=[queue],
             callbacks=[self.on_message]))
        return consumers

    def on_message(self, body, message):
        try:
            print "GOT MESSAGE %r " % message
            logger.info("Began consume message :: got body :: %r " % body)
            db = Db(logger)
            result = db.process_sdp_requests(json.loads(body))
            logger.info("message terminate result :: %r " % result.status_code)
            if result.status_code == 200:
                message.ack()
            message.ack()
        except Exception, e:
            message.requeue()
            logger.info("Exception on message consume:: %r " % e)

app.steps['consumer'].add(AlertConsumerStep)