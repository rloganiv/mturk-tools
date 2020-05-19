import logging

import click

from mtools.client import client


logger = logging.getLogger(__name__)


@click.command()
def accept_all():
    logger.info('Accepting all submitted HITs')
    reviewable_hit_paginator = client.get_paginator('list_reviewable_hits')
    assignment_paginator = client.get_paginator('list_assignments_for_hit')
    for reviewable_hits in reviewable_hit_paginator.paginate():
        for hit in reviewable_hits['HITs']:
            hit_id = hit['HITId']
            iterable = assignment_paginator.paginate(
                HITId=hit_id,
                AssignmentStatuses=['Submitted']
            )
            for assignments in iterable:
                for assignment in assignments['Assignments']:
                    assignment_id = assignment['AssignmentId']
                    logger.info(f'Approving assignment: {assignment_id}')
                    response = client.approve_assignment(AssignmentId=assignment_id)
                    logger.info(f'Response: {response}')





