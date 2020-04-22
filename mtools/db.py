"""
Database Schema, ORM, and related commands.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from mtools.cli import cli
from mtools.config import config


engine = create_engine(config['database']['url'], echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Dataset(Base):
    __tablename__ = 'datasets'

    key = Column(Integer, primary_key=True)

    filename = Column(String)
    md5sum = Column(String)
    eval_type = Column(String)

    instances = relationship('Instance', back_populates='dataset')

    UniqueConstraint(filename, eval_type)


class Instance(Base):
    __tablename__ = 'instances'

    key = Column(Integer, primary_key=True)
    dataset_key = Column(Integer, ForeignKey('datasets.key'))
    question_key = Column(Integer, ForeignKey('questions.key'))

    sentence_good = Column(String)
    sentence_bad = Column(String)

    dataset = relationship('Dataset', back_populates='instances')
    question = relationship('Question', back_populates='instance')


class HitType(Base):
    __tablename__ = 'hittypes'

    key = Column(Integer, primary_key=True)

    short_name = Column(String, unique=True)
    hit_type_id = Column(String, unique=True)
    title = Column(String)
    keywords = Column(String)
    description = Column(String)
    reward = Column(String)

    hits = relationship('Hit', back_populates='hit_type')


class Hit(Base):
    __tablename__ = 'hits'

    key = Column(Integer, primary_key=True)
    hit_type_key = Column(Integer, ForeignKey('hittypes.key'))

    hit_id = Column(String, unique=True)

    hit_type = relationship('HitType', back_populates='hits')
    questions = relationship('Question', back_populates='hit')


class Question(Base):
    __tablename__ = 'questions'

    key = Column(Integer, primary_key=True)
    hit_key = Column(Integer, ForeignKey('hits.key'))
    instance_key = Column(Integer, ForeignKey('instances.key'))

    answer = Column(String)
    choice_a = Column(String)
    choice_b = Column(String)

    hit = relationship('Hit', back_populates='questions')
    instance = relationship('Instance', back_populates='question')


class Qualification(Base):
    __tablename__ = 'qualifications'

    key = Column(Integer, primary_key=True)
    short_name = Column(String, unique=True)
    name = Column(String)
    qualification_type_id = Column(String)


@cli.command()
def init_db():
    Base.metadata.create_all(engine)


@cli.command()
def clear_db():
    Base.metadata.drop_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
