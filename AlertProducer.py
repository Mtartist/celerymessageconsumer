from celery.utils.log import get_task_logger
from celery import Celery
from celery import bootsteps
from kombu import Exchange, Queue
from Publisher import Publisher
from utils import LocalConfigParser
from Db import Db
import time

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
my_queue = Queue(queue_name, Exchange(exchange_name, type='fanout'),
     routing_key)

BROKER_URL = 'amqp://{user}:{password}@{host}:{port}//'.format(
    user=username,
    password=password,
    host=host,
    port=port
)
app = Celery('producer', broker=BROKER_URL)

logger = get_task_logger(__name__)


class AlertProducer(bootsteps.Step):

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
        # The Worker
        # will call stop at shutdown only.
        logger.info('{0!r} is stopping'.format(parent))

    def send_me_a_message(self):
        alerts = self.fetch_active_alerts()
        print "processing active alerts :: %r" % alerts

    def fetch_active_alerts(self):
        try:
            while(True):
                db = Db(logger)
                alerts = db.get_alerts_to_send()
                data_offset = 0
                print "fetched alert to sent %r" % alerts
                if alerts is not None:
                    for alert in alerts:
                        print "flag alert as sent %r" % alert
                        #flag alert as sent to avoid issues
                        if(db.flag_alert_sent(alert)):
                            print "flagged alert as sent proceed fetch subs %r"\
                             % alert
                            if alert.msisdn is not None and alert.msisdn != '':
                                print "send quicksms %r" % alert.msisdn
                                message = {"short_code":
                                             alert.shortcode,
                                            "msisdn": alert.msisdn,
                                            "message": alert.message,
                                            "network": 1,
                                            "alert_type": alert.alert_type_id,
                                            "alert_id": alert.id,
                                            "correlator": str(alert.id) + "_" +
                                             str(alert.msisdn),
                                            "linkId": None}
                                self.publish_rabbit(message)
                            else:
                                #fetch subs 4 this alert
                                sub_count = db.count_alert_subs(alert.service_id)
                                for data_offset in range(sub_count):
                                    subs =\
                                     db.fetch_alert_subscribers(alert.service_id,
                                          data_offset)
                                    print "fetched subs for senting alert\
     %r offset %r" % (subs, data_offset)
                                    if subs is not None:
                                        for sub in subs:
                                            print "looping pushing to queue %r"\
                                             % sub
                                            sub_details =\
                                             db.get_sub_msisdn(sub.profile_id)
                                            message = {"short_code":
                                                 alert.shortcode,
                                                "msisdn": sub_details.msisdn,
                                                "message": alert.message,
                                                "network": sub_details.network_id,
                                                "alert_type": alert.alert_type_id,
                                                "alert_id": alert.id,
                                                "correlator": str(alert.id) + "_" +
                                                 str(sub_details.msisdn),
                                                "linkId": None}
                                            self.publish_rabbit(message)
                                        data_offset += 10000
                else:
                    time.sleep(30)
        except Exception, e:
            print ("error processing alerts to publish :: %r"
             % e)

    def publish_rabbit(self, message):
        print "got message to publish %r" % message
        pyb = Publisher(queue_name, exchange_name, logger)
        inject = pyb.publish(message, routing_key)
        print ("rabbit mq inject result {0!r}".format(inject))

app.steps['worker'].add(AlertProducer)