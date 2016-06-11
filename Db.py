from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool
#from sqlalchemy import func


from utils import LocalConfigParser
import requests
from datetime import datetime
from models import *


class Db():

    APP_NAME = 'MIDNIGHT_2_MIDNIGHT'

    def __del__(self):
        self.close()

    def __init__(self, logger, port=3306):

        self.db_configs = LocalConfigParser.parse_configs("DB")
        self.sdp_configs = LocalConfigParser.parse_configs("SDP")
        self.host = self.db_configs['host']
        self.db = self.db_configs['db_name']
        self.username = self.db_configs['username']
        self.password = self.db_configs['password']
        self.port = self.db_configs['port'] or port

        self.db_uri = self.get_connection_uri()
        self.engine = self.get_engine()
        self.db_session = self.get_db_session()
        self.logger = logger

    def get_connection_uri(self):
        return "mysql+pymysql://{username}:{password}@{host}/{db}".format(
                username=self.username,
                password=self.password,
                host=self.host,
                db=self.db
            )

    def get_engine(self):
        return create_engine(self.db_uri, poolclass=NullPool)

    def get_db_session(self):
        return scoped_session(
                sessionmaker(autocommit=False, autoflush=False,
                     bind=self.engine)
            )

    def get_session(self):
        return self.db_session

    def close(self):
        try:
            self.db_session.remove()
            self.engine.dispose()
        except:
            pass

    def create_inboxes(self, json_data):
        try:
            inbox = Inbox(
                network=json_data.get("network"),
                shortcode=json_data.get("shortcode"),
                msisdn=json_data.get("msisdn"),
                message=json_data.get("message"),
                linkid=json_data.get("linkid"),
                created=json_data.get("created"),
                created_by=json_data.get("created_by")
            )
            self.logger.info("Making inbox values %r " % inbox)
            self.db_session.add(inbox)
            self.db_session.commit()
            trace_id = inbox.inbox_id
            self.logger.info("inbox saved success : %r" % trace_id)
            return inbox
        except Exception as e:
            self.db_session.rollback()
            self.logger.error("Exception creating Inbox, rolled back : %r "
             % e)
            return True
        else:
            self.close()

    def create_profile(self, json_data):
        try:
            profile = Profile(
                profile_id=json_data.get("profile_id"),
                msisdn=json_data.get("msisdn"),
                created=json_data.get("created"),
                status=json_data.get("status"),
                modified=json_data.get("modified"),
                created_by=json_data.get("created_by"),
                network=json_data.get("network"),
            )
            self.logger.info("Making profile values %r " % profile)
            self.db_session.add(profile)
            self.db_session.commit()
            trace_id = profile.profile_id
            self.logger.info("Profile saved success : %r" % trace_id)
            return profile
        except Exception as e:
            self.db_session.rollback()
            self.logger.error("Exception creating profile, rolled back : %r "
             % e)
            return True
        else:
            self.close()

    def terminate_sms_operator(self, json_data):
        self.logger.info("Received sendsmsapi message for terminationation %r"
         % json_data)
        url = self.bulk_configs["url"]

        payload = {
            "msisdn": json_data.get('msisdn'),
            "message": json_data.get('message'),
            "access_code": json_data.get('shortcode')
             or self.bulk_configs["access_code"],
            "linkid": "",
            "short_code": json_data.get('shortcode')
             or self.bulk_configs["bulk_code"],
            "correlator": json_data.get("correlator"),
            "service_id": json_data.get("sdpid")
             or self.bulk_configs["service_id"]
        }

        outbox = self.outbox_message(payload)
        self.logger.info("About to insert outbox_message : %r " % outbox)

        if not outbox:
            self.logger.error("Failed to create outbox message : (%r) "
              % payload)
            return True
        self.logger.info("outbox not null : %s" % outbox.outbox_id)
        payload['correlator'] = outbox.outbox_id

        self.logger.info("Calling SDP URL FOR Sendsms api terminate: (%s, %r) "
         % (url, payload))
        output = None

        try:
            output = requests.post(url, data=payload, timeout=30)
            self.logger.info("Found result from sdp call: (%s) "
             % (output.text, ))
        except requests.exceptions.RequestException as e:
            self.logger.error("Exception attempting to send BULK sendsmsapi \
message : %r data %r " % e, payload)
            output = True

        return output

    def outbox_message(self, message):
        outbox = None
        try:
            self.logger.info("Found create outbox ...")
            outbox = Outbox(
                shortcode=self.bulk_configs["access_code"],
                network=message.get("network"),
                profile_id=None,
                linkid=message.get("linkid"),
                retry_status=0,
                sdp_id=self.bulk_configs["service_id"],
                modified=datetime.now(),
                text=message.get('message'),
                msisdn=message.get("msisdn"),
                date_created=datetime.now(),
                date_sent=datetime.now(),
            )
            self.db_session.add(outbox)
            self.db_session.flush()
            self.db_session.commit()
            self.logger.info("Outbox commit success ...")
            return outbox
        except Exception, e:
            self.logger.error("Problem creating inbox message ...%r" % e)
            self.db_session.rollback()
            self.publish_retry(outbox, 'outbox')
            return None
        else:
            self.close()

    def get_alerts_to_send(self, alert_offset=None):
        try:
            alertQuery = self.db_session.query(Alert)\
                .filter(Alert.sent == 0,
                     Alert.scheduled_time <= datetime.now())\
                .order_by(Alert.created.desc()).limit(10)
            self.logger.info("Alerts raw query :: %s" % alertQuery)
            alerts = alertQuery.all()

            if alerts:
                return alerts
            print "No alerts scheduled to sent"
            self.logger.info("Found no alerts scheduled to sent")
            return None
        except Exception, e:
            self.logger.error("Problem fetching alerts ::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def fetch_alert_subscribers(self, service_id, data_offset):
        subs = None
        try:
            subsQuery = self.db_session.query(Subscriber)\
                .filter_by(Subscriber.service_id == service_id,
                     Subscriber.status == 1)\
                .order_by(Subscriber.created.desc())\
                .limit(10000).offset(data_offset)
            self.logger.info("Subscribers raw query :: %s" % subsQuery)
            subs = subsQuery.all()

            if subs:
                return subs
        except Exception, e:
            self.logger.error("Problem fetching service subscibers ::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def flag_alert_sent(self, alert):
        try:
            alert.sent = 1
            self.db_session.commit()
            return True
        except Exception, e:
            self.logger.error("Problem creating inbox message ...%r" % e)
            self.db_session.rollback()
            self.db_session.remove()
            return None
        else:
            self.close()