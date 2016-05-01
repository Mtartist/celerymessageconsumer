from celery.utils.log import get_task_logger
from celery import Celery
from celery import bootsteps
from kombu import Consumer, Queue
from utils import LocalConfigParser
from Db import Db


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

BROKER_URL = 'amqp://{user}:{password}@{host}:{port}//'.format(
    user=username,
    password=password,
    host=host,
    port=port
)
app = Celery(broker=BROKER_URL)

logger = get_task_logger(__name__)

queue_list = ['pedQueue']


class MyConsumerStep(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        consumers = []
        consumer_config = 50
        for n in range(consumer_config):
            for q in queue_list:
                queue = Queue(q, routing_key=q)
                consumers.append(Consumer(channel, queues=[queue],
                 callbacks=[self.on_message]))
        return consumers

    def on_message(self, body, message):
        try:
            logger.info("Begin consuming message :::: got body :: %r " % body)
            db = Db(logger)
            result = db.terminate_sms_operator()
            if result:
                message.ack()
        except Exception, e:
            logger.info("Exception on message consume:: %r " % e)

app.steps['consumer'].add(MyConsumerStep)