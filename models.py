# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index,\
 Integer, SmallInteger, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Alert(Base):
    __tablename__ = 'alert'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    msisdn = Column(String(200))
    shortcode = Column(String(50))
    content_id = Column(Integer, index=True)
    service_id = Column(ForeignKey(u'service.id'), index=True)
    sent = Column(Integer, nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    alert_type_id = Column(ForeignKey(u'model_type.id'), nullable=False, index=True)
    time_sent = Column(DateTime, index=True)
    created_by_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    alert_type = relationship(u'ModelType')
    created_by = relationship(u'AuthUser')
    service = relationship(u'Service')


class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    email = Column(String(254))
    contact = Column(String(50))
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)


class ArtistRevShare(Base):
    __tablename__ = 'artist_rev_share'
    __table_args__ = (
        Index('artist_id', 'artist_id', 'contract_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    artist_id = Column(ForeignKey(u'artist.id'), nullable=False, index=True)
    contract_id = Column(ForeignKey(u'contract.id'), nullable=False, unique=True)
    rev_share = Column(String(30), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    artist = relationship(u'Artist')
    contract = relationship(u'Contract')


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('group_id', 'group_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False, index=True)
    permission_id = Column(ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    permission = relationship(u'AuthPermission')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('content_type_id', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    content_type_id = Column(ForeignKey(u'django_content_type.id'), nullable=False, index=True)
    codename = Column(String(100), nullable=False)

    content_type = relationship(u'DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime, nullable=False)
    is_superuser = Column(Integer, nullable=False)
    username = Column(String(30), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(75), nullable=False)
    is_staff = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    date_joined = Column(DateTime, nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('user_id', 'user_id', 'group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    user = relationship(u'AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('user_id', 'user_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    permission_id = Column(ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    permission = relationship(u'AuthPermission')
    user = relationship(u'AuthUser')


class BulkSender(Base):
    __tablename__ = 'bulk_sender'
    __table_args__ = (
        Index('name', 'name', 'sdp_access_code', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    sdp_service_id = Column(String(150))
    sdp_access_code = Column(String(50), nullable=False)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)


class BulkSenderClient(Base):
    __tablename__ = 'bulk_sender_client'
    __table_args__ = (
        Index('bulksender_id', 'bulksender_id', 'client_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    bulksender_id = Column(ForeignKey(u'bulk_sender.id'), nullable=False, index=True)
    client_id = Column(ForeignKey(u'client.id'), nullable=False, index=True)

    bulksender = relationship(u'BulkSender')
    client = relationship(u'Client')


class CeleryTaskmeta(Base):
    __tablename__ = 'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    result = Column(String)
    date_done = Column(DateTime, nullable=False)
    traceback = Column(String)
    hidden = Column(Integer, nullable=False, index=True)
    meta = Column(String)


class CeleryTasksetmeta(Base):
    __tablename__ = 'celery_tasksetmeta'

    id = Column(Integer, primary_key=True)
    taskset_id = Column(String(255), nullable=False, unique=True)
    result = Column(String, nullable=False)
    date_done = Column(DateTime, nullable=False)
    hidden = Column(Integer, nullable=False, index=True)


class Client(Base):
    __tablename__ = 'client'
    __table_args__ = (
        Index('name', 'name', 'user_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, unique=True)
    callback_url = Column(String(200), nullable=False)
    subscription_url = Column(String(200), nullable=False)
    active = Column(Integer, nullable=False, index=True)
    credit_units = Column(String(30), nullable=False)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    user = relationship(u'AuthUser')


class ContactGroup(Base):
    __tablename__ = 'contact_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    client_id = Column(ForeignKey(u'client.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    client = relationship(u'Client')


class ContactGroupProfile(Base):
    __tablename__ = 'contact_group_profile'
    __table_args__ = (
        Index('contactgroup_id', 'contactgroup_id', 'profile_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    contactgroup_id = Column(ForeignKey(u'contact_group.id'), nullable=False, index=True)
    profile_id = Column(ForeignKey(u'profile.id'), nullable=False, index=True)

    contactgroup = relationship(u'ContactGroup')
    profile = relationship(u'Profile')


class Content(Base):
    __tablename__ = 'content'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    artist_id = Column(ForeignKey(u'artist.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    artist = relationship(u'Artist')


class ContentService(Base):
    __tablename__ = 'content_service'
    __table_args__ = (
        Index('content_id', 'content_id', 'service_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    content_id = Column(ForeignKey(u'content.id'), nullable=False, index=True)
    service_id = Column(ForeignKey(u'service.id'), nullable=False, index=True)

    content = relationship(u'Content')
    service = relationship(u'Service')


class Contract(Base):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True)
    artist_id = Column(ForeignKey(u'artist.id'), nullable=False, unique=True)
    start_date = Column(DateTime, nullable=False, index=True)
    termination = Column(DateTime, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    artist = relationship(u'Artist')


class DatabaseBackendmessage(Base):
    __tablename__ = 'database_backendmessage'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    direction = Column(String(1), nullable=False, index=True)
    message_id = Column(String(64), nullable=False)
    external_id = Column(String(64), nullable=False)
    identity = Column(String(100), nullable=False)
    text = Column(String, nullable=False)


class DbMessage(Base):
    __tablename__ = 'db_message'

    id = Column(Integer, primary_key=True)
    status = Column(String(1), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    updated = Column(DateTime, index=True)
    sent = Column(DateTime)
    delivered = Column(DateTime)
    direction = Column(String(1), nullable=False, index=True)
    text = Column(String, nullable=False)
    external_id = Column(String(1024), nullable=False)
    in_response_to_id = Column(ForeignKey(u'db_message.id'), index=True)

    in_response_to = relationship(u'DbMessage', remote_side=[id])


class DbTransmission(Base):
    __tablename__ = 'db_transmission'

    id = Column(Integer, primary_key=True)
    message_id = Column(ForeignKey(u'db_message.id'), nullable=False, index=True)
    connection_id = Column(ForeignKey(u'rapidsms_connection.id'), nullable=False, index=True)
    status = Column(String(1), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    updated = Column(DateTime, index=True)
    sent = Column(DateTime)
    delivered = Column(DateTime)

    connection = relationship(u'RapidsmsConnection')
    message = relationship(u'DbMessage')


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime, nullable=False)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)
    content_type_id = Column(ForeignKey(u'django_content_type.id'), index=True)
    object_id = Column(String)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(String, nullable=False)

    content_type = relationship(u'DjangoContentType')
    user = relationship(u'AuthUser')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('app_label', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(String, nullable=False)
    expire_date = Column(DateTime, nullable=False, index=True)


class DjangoSite(Base):
    __tablename__ = 'django_site'

    id = Column(Integer, primary_key=True)
    domain = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)


class DjceleryCrontabschedule(Base):
    __tablename__ = 'djcelery_crontabschedule'

    id = Column(Integer, primary_key=True)
    minute = Column(String(64), nullable=False)
    hour = Column(String(64), nullable=False)
    day_of_week = Column(String(64), nullable=False)
    day_of_month = Column(String(64), nullable=False)
    month_of_year = Column(String(64), nullable=False)


class DjceleryIntervalschedule(Base):
    __tablename__ = 'djcelery_intervalschedule'

    id = Column(Integer, primary_key=True)
    every = Column(Integer, nullable=False)
    period = Column(String(24), nullable=False)


class DjceleryPeriodictask(Base):
    __tablename__ = 'djcelery_periodictask'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    task = Column(String(200), nullable=False)
    interval_id = Column(ForeignKey(u'djcelery_intervalschedule.id'), index=True)
    crontab_id = Column(ForeignKey(u'djcelery_crontabschedule.id'), index=True)
    args = Column(String, nullable=False)
    kwargs = Column(String, nullable=False)
    queue = Column(String(200))
    exchange = Column(String(200))
    routing_key = Column(String(200))
    expires = Column(DateTime)
    enabled = Column(Integer, nullable=False)
    last_run_at = Column(DateTime)
    total_run_count = Column(Integer, nullable=False)
    date_changed = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)

    crontab = relationship(u'DjceleryCrontabschedule')
    interval = relationship(u'DjceleryIntervalschedule')


class DjceleryPeriodictask(Base):
    __tablename__ = 'djcelery_periodictasks'

    ident = Column(SmallInteger, primary_key=True)
    last_update = Column(DateTime, nullable=False)


class DjceleryTaskstate(Base):
    __tablename__ = 'djcelery_taskstate'

    id = Column(Integer, primary_key=True)
    state = Column(String(64), nullable=False, index=True)
    task_id = Column(String(36), nullable=False, unique=True)
    name = Column(String(200), index=True)
    tstamp = Column(DateTime, nullable=False, index=True)
    args = Column(String)
    kwargs = Column(String)
    eta = Column(DateTime)
    expires = Column(DateTime)
    result = Column(String)
    traceback = Column(String)
    runtime = Column(Float(asdecimal=True))
    retries = Column(Integer, nullable=False)
    worker_id = Column(ForeignKey(u'djcelery_workerstate.id'), index=True)
    hidden = Column(Integer, nullable=False, index=True)

    worker = relationship(u'DjceleryWorkerstate')


class DjceleryWorkerstate(Base):
    __tablename__ = 'djcelery_workerstate'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(255), nullable=False, unique=True)
    last_heartbeat = Column(DateTime, index=True)


class Inbox(Base):
    __tablename__ = 'inbox'

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    short_code_id = Column(ForeignKey(u'short_code.id'), nullable=False, index=True)
    link_id = Column(String(250))
    service_id = Column(ForeignKey(u'service.id'), index=True)
    transaction_id = Column(ForeignKey(u'transaction.id'), nullable=False, index=True)
    profile_id = Column(ForeignKey(u'profile.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    profile = relationship(u'Profile')
    service = relationship(u'Service')
    short_code = relationship(u'ShortCode')
    transaction = relationship(u'Transaction')


class KannelDeliveryreport(Base):
    __tablename__ = 'kannel_deliveryreport'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    date_sent = Column(DateTime, nullable=False)
    message_id = Column(String(255), nullable=False)
    identity = Column(String(100), nullable=False)
    sms_id = Column(String(36), nullable=False)
    smsc = Column(String(255), nullable=False)
    status = Column(SmallInteger, nullable=False)
    status_text = Column(String(255), nullable=False)


class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    model = Column(String(100), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)


class MediaFile(Base):
    __tablename__ = 'media_file'

    id = Column(Integer, primary_key=True)
    content_id = Column(ForeignKey(u'content.id'), nullable=False, unique=True)
    file_name = Column(String(120), nullable=False)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    content = relationship(u'Content')


class ModelType(Base):
    __tablename__ = 'model_type'
    __table_args__ = (
        Index('name', 'name', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    model = Column(String(150), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)


class Network(Base):
    __tablename__ = 'network'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)


class Outbox(Base):
    __tablename__ = 'outbox'

    id = Column(Integer, primary_key=True)
    alert_id = Column(ForeignKey(u'alert.id'), nullable=False, index=True)
    text = Column(String, nullable=False)
    msisdn = Column(String(200), index=True)
    content_id_hash = Column(String(100), index=True)
    ref_number = Column(BigInteger)
    transaction_id = Column(ForeignKey(u'transaction.id'), nullable=False, index=True)
    dlr_status = Column(Integer, nullable=False, index=True)
    processed = Column(Integer, nullable=False, index=True)
    instance_id = Column(Integer, nullable=False, index=True)
    sends = Column(Integer, nullable=False, index=True)
    time_sent = Column(DateTime, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    alert = relationship(u'Alert')
    transaction = relationship(u'Transaction')


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    msisdn = Column(String(50), nullable=False, unique=True)
    network_id = Column(ForeignKey(u'network.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    network = relationship(u'Network')


class RapidsmsApp(Base):
    __tablename__ = 'rapidsms_app'

    id = Column(Integer, primary_key=True)
    module = Column(String(100), nullable=False, unique=True)
    active = Column(Integer, nullable=False)


class RapidsmsBackend(Base):
    __tablename__ = 'rapidsms_backend'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)


class RapidsmsConnection(Base):
    __tablename__ = 'rapidsms_connection'
    __table_args__ = (
        Index('backend_id', 'backend_id', 'identity', unique=True),
    )

    id = Column(Integer, primary_key=True)
    backend_id = Column(ForeignKey(u'rapidsms_backend.id'), nullable=False, index=True)
    identity = Column(String(100), nullable=False)
    contact_id = Column(ForeignKey(u'rapidsms_contact.id'), index=True)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)

    backend = relationship(u'RapidsmsBackend')
    contact = relationship(u'RapidsmsContact')


class RapidsmsContact(Base):
    __tablename__ = 'rapidsms_contact'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
    language = Column(String(6), nullable=False)


class RegistrationRegistrationprofile(Base):
    __tablename__ = 'registration_registrationprofile'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, unique=True)
    activation_key = Column(String(40), nullable=False)

    user = relationship(u'AuthUser')


class SdpProduct(Base):
    __tablename__ = 'sdp_product'
    __table_args__ = (
        Index('service', 'service', 'product', unique=True),
    )

    id = Column(Integer, primary_key=True)
    service = Column(String(100), nullable=False)
    product = Column(String(100), nullable=False)
    shortcode_id = Column(ForeignKey(u'short_code.id'), nullable=False, index=True)
    keyword_id = Column(ForeignKey(u'keyword.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    keyword = relationship(u'Keyword')
    shortcode = relationship(u'ShortCode')


class Service(Base):
    __tablename__ = 'service'
    __table_args__ = (
        Index('name_2', 'name', 'service_type_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    client_id = Column(ForeignKey(u'client.id'), nullable=False, index=True)
    backend_name = Column(String(100), nullable=False)
    service_type_id = Column(ForeignKey(u'model_type.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    client = relationship(u'Client')
    service_type = relationship(u'ModelType')


class ShortCode(Base):
    __tablename__ = 'short_code'

    id = Column(Integer, primary_key=True)
    short_code = Column(String(50), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    client_id = Column(ForeignKey(u'client.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    client = relationship(u'Client')


class Subscriber(Base):
    __tablename__ = 'subscriber'
    __table_args__ = (
        Index('service_id', 'service_id', 'profile_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    profile_id = Column(ForeignKey(u'profile.id'), nullable=False, index=True)
    service_id = Column(ForeignKey(u'service.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False, index=True)
    transaction_id = Column(ForeignKey(u'transaction.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    profile = relationship(u'Profile')
    service = relationship(u'Service')
    transaction = relationship(u'Transaction')


class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    profile_id = Column(ForeignKey(u'profile.id'), nullable=False, unique=True)
    status = Column(Integer, nullable=False, index=True)
    remarks = Column(String(200), nullable=False)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)

    profile = relationship(u'Profile')


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    model = Column(String(50), nullable=False)
    foreign_key = Column(Integer, index=True)
    created = Column(DateTime, nullable=False, index=True)
    modified = Column(DateTime, nullable=False, index=True)