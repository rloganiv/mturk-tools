"""
Utilities and Commands for deploying MTurk HITs.
"""
import json
import logging
import random

import click

from mtools.cli import cli
from mtools.db import session_scope
from mtools.db import Dataset, Question, Hit, HitType, Instance
from mtools.question_form import QuestionForm


logger = logging.getLogger(__name__)


def unasked_instances(dataset, n):
    """
    Retrieves up to n unasked instances in the specified dataset.
    """
    with session_scope() as session:
        instances = (
            session.query(Instance)
                   .filter(Instance.dataset == dataset)
                   .filter(Instance.question == None)
                   .limit(n)
                   .all()
        )
    return instances


def create_question(instance, type=None):
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
            question_identifier=question.key,
            choices=[question.choice_a, question.choice_b]
        )
    return question_form


@cli.command()
@click.option('-n', '--num_hits', required=True, type=int)
@click.option('-q', '--questions_per_hit', required=True, type=int)
@click.option('-o', '--overview_filename', type=str, default='templates/overview.json')
@click.argument('hit_type_short_name')
def deploy(hit_type_short_name,
           num_hits,
           questions_per_hit,
           overview_filename):
    with open(overview_filename, 'r') as f:
        overview = json.loads(f)

    with session_scope() as session:
        hit_type = (
            session.query(HitType)
                   .filter(HitType.short_name == hit_type_short_name)
                   .one()
        )
        datasets = session.query(Dataset).all()

    total_questions = num_hits * questions_per_hit
    questions_per_dataset = total_questions / len(datasets)

    instances = []
    reserve = 0
    for dataset in datasets:
        instances_ = unasked_instances(
            dataset,
            questions_per_dataset + reserve
        )
        reserve += questions_per_dataset - len(instances_)







