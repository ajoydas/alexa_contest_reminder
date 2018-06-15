import datetime
import logging
import uuid
import os

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import html5lib
import json
import requests
import objectpath
from collections import OrderedDict
import pytz

import boto3
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


DEBUG = False

def example_run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time))


"""
Developed by
Sajid Samsad
samsadsajid@gmail.com
"""

def process_list_header(_list):
	header = [x.replace('\r', '').replace('\n', '').replace(' ', '') for x in _list]
	header = list(OrderedDict.fromkeys(header))
	return header


def make_chunk(_list, splitter):
	return [_list[i:i+splitter] for i in range(0, len(_list), splitter)]


def call_HackkerRank(url):
	try:
		# query the website and return the html to the variable ‘page’
		request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		page = urlopen(request).read()

		# parse the html using beautiful soup and store in variable `soup`
		soup = BeautifulSoup(page, 'html.parser')

		data = []

		contest_name = soup.findAll('span', {'itemprop': 'name'})[1:]

		start_time = soup.findAll('meta', {'itemprop': 'startDate'})[:len(contest_name)]

		end_time = soup.findAll('meta', {'itemprop': 'endDate'})[:len(contest_name)]

		# the following loop needs to be modified
		for idx in range(0, len(contest_name)):
			data.append(contest_name[idx].text)
			data.append(start_time[idx]['content'])
			data.append(end_time[idx]['content'])

		header = ['CONTEST', 'START TIME', 'END TIME']

		processed_data = make_chunk(data, 3)

		for elem in processed_data:
			start = elem[1]
			end = elem[2]

			local_datetime_start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
			local_datetime_end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')

			tz = pytz.timezone('Asia/Dhaka')

			local = tz.localize(local_datetime_start)
			utc = local.astimezone(pytz.utc)

			elem[1] = utc.isoformat()

			local = tz.localize(local_datetime_end)
			utc = local.astimezone(pytz.utc)

			elem[2] = utc.isoformat()

			elem.append('hackerrank')

		return processed_data
	except Exception as e:
		return None


def call_CodeChef(url):
	try:
		# query the website and return the html to the variable ‘page’
		request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		page = urlopen(request).read()

		# parse the html using beautiful soup and store in variable `soup`
		soup = BeautifulSoup(page, 'html.parser')

		tables = soup.findAll('table', {'class': 'dataTable'})[:2]

		data = [[i.text for i in table.findAll('td')] for table in tables]

		bulk = [j for i in data for j in i]

		processed_data = make_chunk(bulk, 4)
		for dat in processed_data:
			dat.pop(0)

		for elem in processed_data:
			start = elem[1]
			end = elem[2]

			local_datetime_start = datetime.strptime(start, '%d %b %Y %H:%M:%S')
			local_datetime_end = datetime.strptime(end, '%d %b %Y %H:%M:%S')

			tz = pytz.timezone('Asia/Calcutta')

			local = tz.localize(local_datetime_start)
			utc = local.astimezone(pytz.utc)

			elem[1] = utc.isoformat()

			local = tz.localize(local_datetime_end)
			utc = local.astimezone(pytz.utc)

			elem[2] = utc.isoformat()

			elem.append('codechef')

		return processed_data

	except Exception as e:
		return None


def call_TopCoder(url):
	try:
		# query the website and return the html to the variable ‘page’
		page = urlopen(url)

		# parse the html using beautiful soup and store in variable `soup`
		soup = BeautifulSoup(page, 'html.parser')

		# print(soup.prettify())
		data = []

		rows = soup.find('tr', {'class': 'light'})
		# print(rows)
		links = rows.findAll('a')
		for i in links:
			# print(i.text)
			data.append(i.text)

		dat = rows.findAll('td', {'class': 'valueC'})
		for i in dat:
			data.append(i.text)

		processed_data = process_list_header(data)
		processed_data.pop(1)
		processed_data.pop(1)
		processed_data.pop(2)
		processed_data.pop(1)
		processed_data.pop(1)
		processed_data.pop(1)
		processed_data.pop(1)

		dat = []
		dat.append(processed_data)

		for elem in dat:
			start = elem[1]
			end = elem[2]

			local_datetime_start = datetime.strptime(start, '%m.%d.%Y%H:%MEDT')
			local_datetime_end = datetime.strptime(end, '%m.%d.%Y%H:%MEDT')

			tz = pytz.timezone('EST5EDT')

			local = tz.localize(local_datetime_start)
			utc = local.astimezone(pytz.utc)

			elem[1] = utc.isoformat()

			local = tz.localize(local_datetime_end)
			utc = local.astimezone(pytz.utc)

			elem[2] = utc.isoformat()

			elem.append('topcoder')

		return dat


	except Exception as e:
		return None


def call_Codeforces(url):

	name = []

	time = []

	try:
		# query the website and return the html to the variable ‘page’
		page = urlopen(url)

		# parse the html using beautiful soup and store in variable `soup`
		soup = BeautifulSoup(page, 'html.parser')
		# print(soup.findAll('table')[0:1])

		for table in soup.findAll('table')[0:1]:
			for td in table.findAll('td'):
				name.append(td.text)

		name[:] = [x.replace('\r', '').replace('\n', '').replace(' ', '') for x in name]

		name = list(filter(None, name))

		name = make_chunk(name, 5)

		name[:] = [elem[:3] for elem in name]

		for elem in name:
			tx = elem[1]
			# print(tx)
			x = tx[11:16]
			hour1 = int(x[0:2])
			minute1 = int(x[3:])
			# print(hour1, minute1)

			y = elem[2]
			hour2 = int(y[0:2])
			minute2 = int(y[3:])
			# print(hour2, minute2)

			hour = hour1 + hour2
			minute = minute1 + minute2
			if(minute > 60):
				minute = minute - 60
				hour+=1
			# print(hour, minute)

			_temp = str(minute)
			if (len(_temp)) == 1:
				_temp = "0" + _temp
			x = tx[:11]+str(hour)+":"+str(_temp)
			# print(x)

			idx = tx.rfind('/')
			tx = tx[:11] + "-" + tx[11:]
			tx = tx.replace('/', '-')
			local_datetime = datetime.strptime(tx, '%b-%d-%Y-%H:%M')

			tz = pytz.timezone('Europe/Moscow')
			local = tz.localize(local_datetime)
			utc = local.astimezone(pytz.utc)

			elem[1] = utc.isoformat()
			# print(elem[1])
			x = x[:11] + "-" + x[11:]
			x = x.replace('/', '-')
			local_datetime = datetime.strptime(x, '%b-%d-%Y-%H:%M')

			local = tz.localize(local_datetime)
			utc = local.astimezone(pytz.utc)

			elem[2] = utc.isoformat()

			elem.append('codeforces')

		return name

	except Exception as e:
		return None


def call_SpoJ(url):
	try:
		# query the website and return the html to the variable ‘page’
		page = urlopen(url)

		# parse the html using beautiful soup and store in variable `soup`
		soup = BeautifulSoup(page, 'html.parser')

		tables = soup.findAll('table', {'class': 'table-condensed'})[:2]

		data = [[i.text for i in table.findAll('td')] for table in tables]

		bulk = [j for i in data for j in i]

		processed_data = make_chunk(bulk, 3)

		for elem in processed_data:
			elem.append('spoj')

		return processed_data

	except Exception as e:
		return None


def run(event, context):
	for choice in range(1,6):
		if choice == 1:
			url = "http://www.spoj.com/contests/"
			data = call_SpoJ(url)
		elif choice == 2:
			url = "https://codeforces.com/contests"
			data = call_Codeforces(url)
		elif choice == 3:
			url = "https://community.topcoder.com/longcontest/"
			data = call_TopCoder(url)
		elif choice == 4:
			url = "https://www.codechef.com/contests"
			data = call_CodeChef(url)
		elif choice == 5:
			url = "https://www.hackerrank.com/contests"
			data = call_HackkerRank(url)

		print(data)
		if(data == None):
			print("No data for updating.")
		else:
			update_db(data)


# After Refetching
def update_db(updated_data):
	if len(updated_data) == 0:
		print("No data found!")
		return

	website = updated_data[0][3]
	print("Updating for website:"+ website)

	table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
	response = table.query(
	    IndexName='website_index',
	    KeyConditionExpression=Key('website').eq(website)
	)
	items = response['Items']
	# print(items)

	matched_data = [False]*len(updated_data)

	for item in items:
	    matched = False
	    for indx, i in enumerate(updated_data):
	        if i[0] == item['name']: 
	            matched = True
	            matched_data[indx] = True
	            print(item)
	            if i[1] != item['startdate'] or i[2] != item['enddate']:
	#                 update
	                table.update_item(
	                    Key={
	                        'id': item['id'],
	                    },
	                    UpdateExpression='SET startdate = :startdate, enddate = :enddate',
	                    ExpressionAttributeValues={
	                        ':startdate': i[1],
	                        ':enddate': i[2]
	                    }
	                )

	    if matched is False:
	#         delete
	        table.delete_item(
	            Key={
	                'id': item['id']
	            }
	        )

	# print(matched_data)

	with table.batch_writer() as batch:
	    for indx in range(len(matched_data)):
	        if matched_data[indx] is False:
	#             add
	            i = updated_data[indx]
	            batch.put_item(
	            Item={
	                'id': str(uuid.uuid4()),
	                'name': i[0],
	                'startdate': i[1],
	                'enddate': i[2],
	                'website': i[3],
	            }
	        )
