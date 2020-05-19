"""
Utilities and Commands for deploying MTurk HITs.
"""
import json
import logging
import random

import click

from mtools.client import client
from mtools.db import session_scope
from mtools.db import Dataset, Question, Hit, HitType, Instance
from mtools.question_form import QuestionForm


logger = logging.getLogger(__name__)


def unasked_instances(session, dataset, n):
    """
    Retrieves up to n unasked instances in the specified dataset.
    """
    instances = (
        session.query(Instance)
                .filter(Instance.dataset == dataset)
                .filter(Instance.question == None)
                .limit(n)
                .all()
    )
    return instances


def get_instances(session, datasets, questions_per_dataset):
    # Try to get the requested number of questions; if a dataset is exhausted then allocate more
    # questions from the next dataset. Break into HIT-sized chunks at the end.
    instances = []
    reserve = 0
    for dataset in datasets:
        instances_ = unasked_instances(
            session,
            dataset,
            questions_per_dataset + reserve
        )
        reserve += questions_per_dataset - len(instances_)
        instances.extend(instances_)
    random.shuffle(instances)
    return instances


def chunk_list(x, chunk_size):
    """Break a list into chunks"""
    return [x[i:i + chunk_size] for i in range(0, len(x), chunk_size)]


def create_question(instance):
    """
    Creates a question from an instance.
    """
    correct = instance.sentence_good
    incorrect = instance.sentence_bad
    answer = random.choice(['a', 'b'])
    noflip = answer == 'a'
    choice_a = correct if noflip else incorrect
    choice_b = incorrect if noflip else correct
    question = Question(
        instance=instance,
        answer=answer,
        choice_a=choice_a,
        choice_b=choice_b
    )
    return question


def create_question_form(overview, questions):
    """
    Creates a question form from an overview and a list of questions.
    """
    question_form = QuestionForm()
    question_form.add_overview(**overview)
    for question in questions:
        question_form.add_multiple_choice_question(
            question_identifier=str(question.key),
            choices=[question.choice_a, question.choice_b]
        )
    return question_form


@click.command()
@click.option('-n', '--num_hits', required=True, type=int)
@click.option('-q', '--questions_per_hit', required=True, type=int)
@click.option('--max_assignments', type=int, default=3)
@click.option('--lifetime_in_seconds', type=int, default=604800)  # Default: 1 week
@click.option('--overview_filename', type=str, default='templates/overview.json')
@click.argument('hit_type_short_name')
def deploy(hit_type_short_name,
           num_hits,
           questions_per_hit,
           max_assignments,
           lifetime_in_seconds,
           overview_filename):
    logger.info('Deploying HITs w/ type "%s"', hit_type_short_name)
    with open(overview_filename, 'r') as f:
        overview = json.load(f)

    with session_scope() as session:
        hit_type = (
            session.query(HitType)
                   .filter(HitType.short_name == hit_type_short_name)
                   .one()
        )
        datasets = session.query(Dataset).all()
        total_questions = num_hits * questions_per_hit
        questions_per_dataset = total_questions / len(datasets)
        instances = get_instances(session, datasets, questions_per_dataset)
        instance_chunks = chunk_list(instances, questions_per_hit)
        if num_hits > len(instance_chunks):
            logger.warn(
                'Attempting to create %i HITs instead of %i',
                len(instance_chunks),
                num_hits
            )
        for instance_chunk in instance_chunks:
            questions = [create_question(i) for i in instance_chunk]
            session.commit()  # So the keys exist
            question_form = create_question_form(overview, questions)
            response = client.create_hit_with_hit_type(
                HITTypeId=hit_type.hit_type_id,
                MaxAssignments=max_assignments,
                LifetimeInSeconds=604800,  # 1 week
                Question=question_form.tostring(),
            )
            logger.info("Create HIT with HITType response: %s", response)
            hit_id = response['HIT']['HITId']
            hit = Hit(
                hit_id=hit_id,
                hit_type=hit_type
            )
            for question in questions:
                question.hit = hit
            session.add(hit)
            session.add_all(questions)
            session.commit()  # Don't want to rollback successful launches
