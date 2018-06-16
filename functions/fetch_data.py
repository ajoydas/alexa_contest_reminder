import logging
import os
from datetime import datetime
from pprint import pprint

import boto3
import dateutil.parser
import pytz

utc=pytz.UTC
dynamodb = boto3.resource('dynamodb')
sites_available = ['spoj','codechef','codeforces','topcoder','hackerrank']
links_parsed = {
    'spoj': 'http://www.spoj.com/contests/',
    'codechef': 'https://www.codechef.com/contests',
    'codeforces': 'https://codeforces.com/contests',
    'topcoder': 'https://community.topcoder.com/longcontest/',
    'hackerrank': 'https://www.hackerrank.com/contests'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_site_data(site, count):
    # site="SpoJ"
    # count=0
    utcnow = datetime.utcnow().isoformat()
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    response = table.query(
        IndexName='website_index',
        KeyConditionExpression='website = :website and enddate >= :enddate',
        ExpressionAttributeValues= {
            ':website': site,
            ':enddate': utcnow
        }
    )
    items = response['Items']
    # pprint(items)

    fetched_data = []
    for item in items:
        startdate = dateutil.parser.parse(item['startdate']).replace(tzinfo=utc)
        enddate = dateutil.parser.parse(item['enddate']).replace(tzinfo=utc)

        fetched_data.append([item['name'] ,startdate, enddate, item['website']])

    fetched_data = sorted(fetched_data, key=lambda x: x[2], reverse=False)
    # pprint(fetched_data)

    if len(fetched_data) == 0:
        return []

    if len(fetched_data) < count:
        return fetched_data

    return fetched_data[:count]


def get_all_site_data(count):
    fetched_data = []
    for site in sites_available:
        contests = get_site_data(site, count)
        if len(contests) != 0:
            for contest in contests:
                fetched_data.append(contest)

    # pprint(fetched_data)
    fetched_data = sorted(fetched_data, key=lambda x: x[2], reverse=False)
    pprint(fetched_data)

    if len(fetched_data) == 0:
        return []

    if len(fetched_data) < count:
        return fetched_data

    return fetched_data[:count]