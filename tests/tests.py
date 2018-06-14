
import datetime
import logging
import uuid
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import boto3
dynamodb = boto3.resource('dynamodb')

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time))

def test_db(event, context):

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    data = [
    [str(uuid.uuid4()), 'codechef', 'Round 1', '2018-06-18T07:00:00.000Z', '2018-06-18T09:00:00.000Z'],
    [str(uuid.uuid4()), 'codechef', 'Round 2', '2018-06-20T10:45:00.000Z','2018-06-20T11:45:00.000Z'],
    [str(uuid.uuid4()), 'topcoder', 'Round 3', '2018-06-18T07:00:00.000Z', '2018-06-18T09:00:00.000Z'],
    [str(uuid.uuid4()), 'topcoder', 'Round 4', '2018-06-20T10:45:00.000Z', '2018-06-20T11:45:00.000Z']
       ]

    with table.batch_writer() as batch:
        for i in data:
            batch.put_item(
                Item={
                    'id': i[0],
                    'website': i[1],
                    'name': i[2],
                    'startdate': i[3],
                    'enddate': i[4],
                }
            )

    logger.info(table.scan())
