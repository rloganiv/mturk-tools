"""
Utilities and Commands for evaluating results
"""
from collections import defaultdict

import xml.etree.ElementTree as xml

from mtools.client import client
from mtools.db import session_scope
from mtools.db import Hit, HitType, Question, Qualification


NAMESPACE = {
    'mturk': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd'
}


def submitted_assignments(hit_ids):
    for hit_id in hit_ids:
        response = client.list_assignments_for_hit(
            HITId=hit_id,
            MaxResults=100,
            AssignmentStatuses=['Submitted']
        )
        for assignment in response['Assignments']:
            yield assignment
        while 'NextToken' in response:
            response = client.list_assignments_for_hit(
                HITId=hit_id,
                NextToken=response['NextToken'],
                MaxResults=100,
                AssignmentStatuses=['Submitted', 'Approved']
            )
            for assignment in response['Assignments']:
                yield assignment


def parse_answer_xml(answer_xml):
    root = xml.fromstring(answer_xml)
    answers = root.findall('mturk:Answer', NAMESPACE)
    results = []
    for answer in answers:
        question_key = answer.find('mturk:QuestionIdentifier', NAMESPACE)
        selected = answer.find('mturk:SelectionIdentifier', NAMESPACE)
        results.append((int(question_key.text), selected.text))
    return results


def reject_assignment(assignment, feedback):
    """
    Reject assignment and assign bad-worker qualification to worker.
    """
    client.reject_assignment(
        AssignmentId=assignment['AssignmentId'],
        RequesterFeedback=feedback
    )
    # with session_scope() as session:
    #     qualification = (
    #         session.query(Qualification)
    #                .filter(Qualification.short_name == 'bad-worker')
    #                .one()
    #     )
    #     qualification_type_id = qualification.qualification_type_id
    # client.associate_qualification_with_worker(
    #     QualificationTypeId=qualification_type_id,
    #     WorkerId=assignment['WorkerId'],
    #     IntegerValue=1,
    #     SendNotification=False
    # )


def evaluate(hit_type_short_name):
    # Get the HIT ids
    with session_scope() as session:
        hit_type = (
            session.query(HitType)
                   .filter(HitType.short_name == hit_type_short_name)
                   .one()
        )
        hits = session.query(Hit).filter(Hit.hit_type == hit_type).all()
        hit_ids = [hit.hit_id for hit in hits]
    print(hit_ids)

    turker_correct = defaultdict(int)
    turker_total = defaultdict(int)
    db_correct = defaultdict(int)
    db_total = defaultdict(int)
    question_correct = defaultdict(int)
    question_total = defaultdict(int)
    for assignment in submitted_assignments(hit_ids):
        print(f"--worker-id {assignment['WorkerId']} --assignment-id {assignment['AssignmentId']}")
        answers = parse_answer_xml(assignment['Answer'])

        # Check for nefarious answers
        all_a = all(map(lambda x: x[1]=='a', answers))
        all_b = all(map(lambda x: x[1]=='b', answers))
        if all_a or all_b:
            # reject_assignment(
            #     assignment,
            #     'We detected no variability in your answers.'
            # )
            continue

        # TODO: Lazy. Clean up.
        with session_scope() as session:
            for question_id, answer in answers:
                question = (
                    session.query(Question)
                           .filter(Question.key == question_id)
                           .one()
                )
                correct = answer == question.answer
                worker_id = assignment['WorkerId']
                dataset = question.instance.dataset.filename
                db_correct[dataset] += correct
                db_total[dataset] += 1
                turker_correct[worker_id] += correct
                turker_total[worker_id] += 1
                question_correct[question_id] += correct
                question_total[question_id] += 1

    for key in db_correct:
        print(f'{key}:: {db_correct[key] / db_total[key]}')
    for key in turker_correct:
        print(f'{key}:: {turker_correct[key] / turker_total[key]}')
    for key in question_correct:
        print(f'{key}:: {question_correct[key]} / {question_total[key]}')



        # add_answers(answers)
        # client.approve_assignment(
            # AssignmendId=assignment['AssignmentId'],
            # RequesterFeedback='Thank you for your work!'
        # )


if __name__ == '__main__':
    evaluate('qualified_eval')

