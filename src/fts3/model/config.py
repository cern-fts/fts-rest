from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy import Integer, String
from sqlalchemy.orm import relation
from sqlalchemy import or_, and_

from base import Base


class  ConfigAudit(Base):
    __tablename__ = 't_config_audit'

    datetime = Column(DateTime, primary_key=True)
    dn       = Column(String(1024), primary_key=True)
    config   = Column(String(4000), primary_key=True)
    action   = Column(String(100), primary_key=True)

    def __str__(self):
        return "%s %s: %s" % (self.datetime, self.action, self.config)


class LinkConfig(Base):
    __tablename__ = 't_link_config'

    source            = Column(String, primary_key=True)
    destination       = Column(String, primary_key=True)
    state             = Column(String)
    symbolicname      = Column(String)
    nostreams         = Column(Integer)
    tcp_buffer_size   = Column(Integer)
    urlcopy_tx_to     = Column(Integer)
    no_tx_activity_to = Column(Integer)
    auto_protocol     = Column(String(3))

    share_config =\
        relation('ShareConfig', backref='link_config',
                 primaryjoin='ShareConfig.source == LinkConfig.source and '
                             'ShareConfig.destination == LinkConfig.destination',
                 foreign_keys=(source, destination),
                 uselist=False,
                 lazy='eager')

    def __str__(self):
        return "%s => %s" % (self.source, self.destination)


class Se(Base):
    __tablename__ = 't_se'

    se_id_info = Column(Integer)
    name       = Column(String, primary_key=True)
    endpoint   = Column(String)
    se_type    = Column(String)
    site       = Column(String)
    state      = Column(String)
    version    = Column(String)
    host       = Column(String)
    se_transfer_type     = Column(String)
    se_transfer_protocol = Column(String)
    se_control_protocol  = Column(String)
    gocdb_id   = Column(String)

    source_on =\
        relation('LinkConfig', backref='source_se',
                 primaryjoin=and_(LinkConfig.source == name,
                                  LinkConfig.destination != '*'),
                 foreign_keys=name, uselist=True, lazy='dynamic')

    destination_on =\
        relation('LinkConfig', backref='destination_se',
                 primaryjoin=and_(LinkConfig.destination == name,
                                  LinkConfig.source != '*'),
                 foreign_keys=name, uselist=True, lazy='dynamic')

    standalone_source =\
        relation('LinkConfig', backref=None,
                 primaryjoin=and_(LinkConfig.source == name,
                                  LinkConfig.destination == '*'),
                 foreign_keys=name, lazy='dynamic')

    standalone_destination =\
        relation('LinkConfig', backref=None,
                 primaryjoin=and_(LinkConfig.destination == name,
                                  LinkConfig.source == '*'),
                 foreign_keys=name, lazy='dynamic')

    def __str__(self):
        return self.name


class ShareConfig(Base):
    __tablename__ = 't_share_config'

    source      = Column(String, primary_key=True)
    destination = Column(String, primary_key=True)
    vo          = Column(String, primary_key=True)
    active      = Column(Integer)

    __table_args__ = (ForeignKeyConstraint(['source', 'destination'],
                                           [LinkConfig.source,
                                            LinkConfig.destination]),)

    def __str__(self):
        return "%s: %s => %s" % (self.vo, self.source, self.destination)


class Group(Base):
    __tablename__ = 't_group_members'

    groupname = Column(String, primary_key=True)

    def __str__(self):
        return self.groupname


class Member(Base):
    __tablename__ = 't_group_members'
    __table_args__ = ({'useexisting': True})

    groupname = Column(String, primary_key=True)
    member    = Column(String, primary_key=True)

    def __str__(self):
        return "%s/%s" % (self.groupname, self.member)
