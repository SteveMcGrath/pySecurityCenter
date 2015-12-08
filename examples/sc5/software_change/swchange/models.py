from sqlalchemy import Column, Integer, Text, Date, DateTime, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from copy import copy
import sys


Base = declarative_base()
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(engine)


class AssetList(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    hosts = relationship('Host', backref='assetlist')
AssetList.metadata.create_all(engine)


class Host(Base):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    ip = Column(Text)
    name = Column(Text)
    dns = Column(Text)
    cpe = Column(Text)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    entries = relationship('Entry', backref='host')

    def changes(self, start=None, end=None):
        sys.stdout.write('running changelog for %s/%s...' % (self.id, self.dns))
        sys.stdout.flush()
        entries = self.entries
        dates = sorted(set([e.timestamp for e in entries]))
        changes = []
        for date in reversed(dates):
            if dates.index(date) == 0: continue
            current = [e for e in entries if e.timestamp == date]
            last = [e for e in entries if e.timestamp == dates[dates.index(date) - 1]]
            for item in current:
                if item.name not in [e.name for e in last]:
                    i = copy(item)
                    i.change = 'installed'
                    changes.append(i)
            for item in last:
                if item.name not in [e.name for e in current]:
                    i = copy(item)
                    i.change = 'removed'
                    i.timestamp = date
                    changes.append(i)
        sys.stdout.write('\tdone\n')
        sys.stdout.flush()
        return sorted(changes, key=lambda c: c.timestamp)
Host.metadata.create_all(engine)


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'))
    patch = Column(Text)
    name = Column(Text)
    version = Column(Text)
    date = Column(Date)
    timestamp = Column(DateTime)
Entry.metadata.create_all(engine)
