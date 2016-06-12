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
        self.bulk_configs = LocalConfigParser.parse_configs("SDP_CONFIGS")
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

    def create_profile(self, json_data):
        try:
            profile = Profile(
                msisdn=json_data.get("msisdn"),
                network_id=json_data.get("network") or 1,
                created=datetime.now(),
                modified=datetime.now()
            )
            self.logger.info("Making profile values %r " % profile)
            self.db_session.add(profile)
            self.db_session.commit()
            trace_id = profile.id
            self.logger.info("Profile saved success : %r" % trace_id)
            return profile
        except Exception as e:
            self.db_session.rollback()
            self.logger.error("Exception creating profile, rolled back : %r "
             % e)
            return True
        else:
            self.close()

    def sent_auto_reponse(self, json_data):
        self.logger.info("Received autoresponse request for terminationation %r"
         % json_data)
        url = self.sdp_configs["url"]

        payload = {
            "msisdn": json_data.get('msisdn'),
            "message": json_data.get('message'),
            "linkid": json_data.get('linkId'),
            "short_code": json_data.get('shortcode')
             or self.sdp_configs["mo_code"],
            "correlator": json_data.get("correlator"),
            "service_id": json_data.get("sdpid")
             or self.sdp_configs["mo_service_id"],
        }

        outbox = self.outbox_message(payload)
        self.logger.info("Created outbox_message : %r " % outbox)

        if not outbox:
            self.logger.error("Failed to create outbox message : (%r) "
              % payload)
            return True
        self.logger.info("outbox not null : %s" % outbox.id)
        payload['correlator'] = outbox.id

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

    def terminate_sms_operator(self, json_data):
        self.logger.info("Received sendsms request for terminationation %r"
         % json_data)
        url = self.sdp_configs["url"]

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
             or self.bulk_configs["service_id"],
            "alert_id": json_data.get("alert_id")
        }

        outbox = self.outbox_message(payload)
        self.logger.info("Created outbox_message : %r " % outbox)

        if not outbox:
            self.logger.error("Failed to create outbox message : (%r) "
              % payload)
            return True
        self.logger.info("outbox not null : %s" % outbox.id)
        payload['correlator'] = outbox.id

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
            trx = self.create_transaction('OUTBOX')
            self.logger.info("Found create outbox ...")
            outbox = Outbox(
                alert_id=message.get("alert_id"),
                text=message.get('message'),
                msisdn=message.get("msisdn"),
                content_id_hash=message.get("content_id_hash") or None,
                ref_number=message.get("correlator"),
                transaction_id=trx.id,
                dlr_status=None,
                processed=1,
                instance_id=1,
                sends=1,
                time_sent=datetime.now(),
                created=datetime.now(),
                modified=datetime.now()
            )
            self.db_session.add(outbox)
            self.db_session.commit()
            self.logger.info("Outbox commit success ...")
            return outbox
        except Exception, e:
            self.logger.error("Problem creating outbox message ...%r" % e)
            self.db_session.rollback()
            return None
        else:
            self.close()

    def create_inbox(self, msg, sc_service):
        trx = None
        try:
            trx = self.create_transaction('INBOX')
            self.logger.info("Found create inbox ...")
            inbox = Inbox(
                message=msg.get("message"),
                msisdn=msg.get("msisdn"),
                short_code_id=sc_service.short_code_id,
                link_id=msg.get("linkid"),
                service_id=sc_service.service_id,
                transaction_id=trx.id,
                profile_id=sc_service.profile_id,
                created=datetime.now(),
                modified=datetime.now()
            )
            self.db_session.add(inbox)
            self.logger.info("Inbox commit success ...")
            return trx
        except Exception, e:
            self.logger.error("Problem creating inbox message ...%r" % e)
            self.db_session.rollback()
            return None
        else:
            self.close()

    def create_transaction(self, trx_model):
        trx = None
        try:
            self.logger.info("Found create transaction ...")
            trx = Transaction(
                model=trx_model,
                foreign_key=None,
                created=datetime.now(),
                modified=datetime.now()
            )
            self.db_session.add(trx)
            self.db_session.flush()
            self.logger.info("Transaction commit success ...")
            return trx
        except Exception, e:
            self.logger.error("Problem creating inbox message ...%r" % e)
            self.db_session.rollback()
            return None
        else:
            self.close()

    def create_subscription(self, data, profile_id, service):
        sub = None
        try:
            trx = self.create_transaction('SUBSCRIBER')
            self.logger.info("Found create subscription ...")
            sub = Subscriber(
                profile_id=profile_id,
                service_id=service,
                status=1,
                transaction_id=trx.id,
                created=datetime.now(),
                modified=datetime.now()
            )
            self.db_session.add(sub)
            self.db_session.flush()
            self.logger.info("Subscription commit success ...")
            return sub
        except Exception, e:
            self.logger.error("Problem creating subscription ...%r" % e)
            self.db_session.rollback()
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

    def get_shortcode_local_service(self, message):
        try:
            sdp_service = message.get('sdp_service_id')
            sc_query = self.db_session.query(SdpProduct, ShortCode,
                 Keyword, Service)\
                 .join(ShortCode, ShortCode.id == SdpProduct.shortcode_id,
                      Keyword.id == SdpProduct.keyword_id,
                       Service.keyword_id == SdpProduct.keyword_id)\
                .filter(SdpProduct.service == sdp_service)
            self.logger.info("get shortcode service raw query :: %s" % sc_query)
            sc_data = sc_query.first()

            if sc_data:
                return sc_data
            self.logger.info("Found shortcode :: %s and local service :: %s"
             % (sc_data.short_code, sc_data.service_id))
            return None
        except Exception, e:
            self.logger.error("Problem fetching alerts ::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def process_sdp_requests(self, body, message):
        try:
            #create profile
            if message.get('exchange') == 'SyncMNOQUEUE_EX':
                #fetch shortcode/local service
                sc_service = self.get_shortcode_local_service(body)
                if body.get("sdpAction") == 2:
                    #unsubscribe
                    return self.unsubscribe(sc_service, body)
                else:
                    #subscribe
                    return self.create_subscription(data, sc_service.profile_id,
                         sc_service.service_id)
            elif message.get('exchange') == 'NotifyMNOQUEUE_EX':
                #create inbox
                result = self.create_inbox(body)
                #send auto response
                if result:
                    return False
                return self.sent_auto_reponse(body)
            elif message.get('exchange') == 'BulkStopExchange':
                #create inbox
                result = self.create_inbox(body)
                if result:
                    return False
                return self.remove_profile_from_contacts(body)
            elif message.get('exchange') == 'DLRMNOQUEUEU_EX':
                #update outbox
                return self.update_outbox_message(body)
            self.logger.info("Processing sdp request %r" % body)
            return None
        except Exception, e:
            self.logger.error("Problem process_sdp_requests :: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def remove_profile_from_contacts(self, msg):
        try:
            profile_data = self.fetch_profile_data(msg)
            contact = self.fetch_bulk_contacts(profile_data)
            self.logger.error("got contact to remove :: %r" % contact)
            if contact:
                self.db_session.delete(contact)
                self.db_session.commit()
            return True
        except Exception, e:
            self.logger.error("Problem to remove bulk contact :: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def unsubscribe(self, sc_service, body):
        try:
            profile_data = self.fetch_profile_data(body)
            sub_data = self.fetch_subscriber_data(self, profile_data.id)
            for data in sub_data:
                if sub_data.service_id == sc_service.service_id:
                    sub_data.status = 0
                    self.db_session.commit()
            return True
        except Exception, e:
            self.logger.error("Problem to unsubscribe :: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def fetch_profile_data(self, body):
        try:
            profileQry = self.db_session.query(Profile)\
                .filter(Profile.msisdn == body.get("msisdn"))
            self.logger.info("Subscribers raw query :: %s" % profileQry)
            profile_data = profileQry.all()
            if profile_data:
                return profile_data
        except Exception, e:
            self.logger.error("Problem fetching profile::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def update_outbox_message(self, json):
        try:
            outboxQry = self.db_session.query(Outbox)\
                .filter(Outbox.id == body.get("correlator"))
            self.logger.info("Outboxes raw query :: %s" % outboxQry)
            outbox_data = outboxQry.all()
            if outbox_data:
                outbox_data.dlr_status = json.get("status")
                outbox_data.ref_number = json.get("trace_id")
                self.db_session.commit()
                return True
            return False
        except Exception, e:
            self.logger.error("Problem fetching outbox::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def fetch_bulk_contacts(self, pdata):
        try:
            contactQry = self.db_session.query(ContactGroupProfile)\
                .filter(ContactGroupProfile.profile_id == pdata.id)
            self.logger.info("Bulk contacts raw query :: %s" % contactQry)
            contact_data = contactQry.all()
            if contact_data:
                return contact_data
        except Exception, e:
            self.logger.error("Problem fetching bulk contact::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def fetch_subscriber_data(self, profile_id):
        try:
            subQry = self.db_session.query(Subscriber)\
                .filter(Subscriber.profile_id == profile_id)
            self.logger.info("Subscriber raw query :: %s" % subQry)
            subscriber_data = subQry.all()
            if subscriber_data:
                return subscriber_data
        except Exception, e:
            self.logger.error("Problem fetching subscription::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def fetch_alert_subscribers(self, service_id, data_offset):
        subs = None
        try:
            subsQuery = self.db_session.query(Subscriber)\
                .filter(Subscriber.service_id == service_id,
                     Subscriber.status == 1).limit(10000).offset(data_offset)
            self.logger.info("Subscribers raw query :: %s" % subsQuery)
            subs = subsQuery.all()

            if subs:
                return subs
        except Exception, e:
            self.logger.error("Problem fetching service subscibers ::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def get_sub_msisdn(self, profile_id):
        try:
            subQuery = self.db_session.query(Profile)\
                .filter(Profile.id == profile_id)
            self.logger.info("Profile data raw query :: %s" % subQuery)
            sub_data = subQuery.first()
            self.logger.info("Profile msisdn %r" % sub_data.msisdn)
            return sub_data
        except Exception, e:
            self.logger.error("Problem getting profile msisdn ::: %r" % e)
            self.db_session.remove()
        else:
            self.close()

    def count_alert_subs(self, service_id):
        try:
            subsQuery = self.db_session.query(Subscriber)\
                .filter(Subscriber.service_id == service_id,
                     Subscriber.status == 1)
            self.logger.info("Subscribers count raw query :: %s" % subsQuery)
            subs_total = subsQuery.count()
            self.logger.info("Subscribers count %r" % subs_total)
            return subs_total
        except Exception, e:
            self.logger.error("Problem counting service subscibers ::: %r" % e)
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