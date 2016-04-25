from amqplib import client_0_8 as amqp
from utils import LocalConfigParser
#from dicttoxml import dicttoxml
import json
#from bootstrap import logger


class Publisher(object):

    def __init__(self, queue_name, exchange_name, logger):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.configs = LocalConfigParser.parse_configs("RABBIT")
        self.sdp_configs = LocalConfigParser.parse_configs("SDP")
        self.logger = logger

    def get_queue_message(self, message):
        queue_message = {
            "shortCode": message.get("short_code"),
            "msisdn": message.get("msisdn"),
            "message": message.get("message"),
            "network": message.get("network"),
            "sdpId": message.get("sdp_id"),
            "alert_type": message.get("alert_type"),
            "correlator": message.get("correlator"),
            "linkId": message.get("link_id")
            }

        return queue_message

    def publish(self, message, routing_key):

        q_message = self.get_queue_message(message)

        print("FOUND MESSAGE posting to Q: %r "
         % q_message.get("mo"))

        try:
            conn = amqp.Connection(host=self.configs['rabbithost'],
                userid=self.configs['rabbitusername'],
                password=self.configs['rabbitpassword'],
                virtual_host=self.configs['rabbitvhost'] or "/",
                insist=False)
        except Exception, e:
            print("Error attempting to get Rabbit Connection: %r "
             % e)
            return None

        print("Connection to rabbit established ...")
        try:
            print("Attempting to queue message")
            ch = conn.channel()

            ch.exchange_declare(exchange=self.exchange_name, type="fanout",
                 durable=True, auto_delete=False)

            ch.queue_declare(queue=self.queue_name, durable=True,
                 exclusive=False, auto_delete=False)
            ch.queue_bind(queue=self.queue_name, exchange=self.exchange_name,
                 routing_key=routing_key)

            msg = amqp.Message(json.dumps(q_message))
            msg.properties["content_type"] = "text/plain"
            msg.properties["delivery_mode"] = 2

            ch.basic_publish(exchange=self.exchange_name,
                             routing_key=routing_key,
                             msg=msg)

            print("Message queued success ... ")
        except Exception, e:
            print("Error attempting to publish to Rabbit: %r " % e)
            conn.close()
        else:
            ch.close()
            conn.close()
