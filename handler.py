import logging
import boto3
import logging
import uuid
import os
from pprint import pprint
from datetime import datetime
import dateutil.parser
import pytz


from boto3.dynamodb.conditions import Key, Attr

utc=pytz.UTC
dynamodb = boto3.resource('dynamodb')
sites_available = ['spoj','codechef','codeforces','topcoder','hackerrank']

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



##############################
# Builders
##############################


def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech

def build_SSMLSpeech(body):
    speech = {}
    speech['type'] = 'SSML'
    speech['ssml'] = '<speak>'+body+'</speak>'
    return speech


def build_response(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response


def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card


##############################
# Responses
##############################


def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_response(speechlet, session_attributes=session_attributes)


def statement(title, speak_body, card_body=None):
    if(card_body is None):
        card_body = speak_body

    speechlet = {}
    speechlet['outputSpeech'] = build_SSMLSpeech(speak_body)
    speechlet['card'] = build_SimpleCard(title, card_body)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)


def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(message)



##############################
# Program Entry
##############################


def lambda_handler(event, context):
    print(event)
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)

    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)
    
    else:
        return on_error(event, context)



##############################
# Routing
##############################

def intent_router(event, context):
    intent = event['request']['intent']['name']

    # Custom Intents

    if intent == "AllSiteIntent":
        return all_site_intent(event, context)

    if intent == "SingleSiteIntent":
        return single_site_intent(event, context)

    if intent == "SingleSiteAllContestIntent":
        return single_site_all_contest_intent(event, context)

    # Required Intents
    if intent == "AMAZON.CancelIntent":
        return cancel_intent()

    if intent == "AMAZON.HelpIntent":
        return help_intent()

    if intent == "AMAZON.StopIntent":
        return stop_intent()


##############################
# Custom Intents
##############################
def single_site_intent(event, context):
    site = event['request']['intent']['slots']['site']['value']
    print("You have selected "+site+" website")

    if (site in sites_available) == False:
        speak_response = "Sorry, didn't recognize the website name. Please try again."
        return statement("Contest Details:", speak_response)

    data  = get_site_data(site, 1)
    site = site.title()
    
    if(len(data)) == 0:
        speak_response = "There is no contest available now on "+ site
        card_response = speak_response
    else:
        contest_name = data[0][0]
        startdate_string =  data[0][1].strftime('%B %d, %Y, %I %M %p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I %M %p')
        speak_response = "The next contest on "+site+" is <prosody volume='x-loud' rate='slow'>"\
                    + contest_name +"</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> "\
                    + enddate_string + ", <say-as interpret-as='cardinal'>"+endtime_string+"</say-as>"
        card_response = "Site: "+ site +"\n"+\
                        "Contest: "+ contest_name +"\n"+\
                        "Start Time: "+ startdate_string +"\n"+\
                        "End Time: " + enddate_string + ", "+ endtime_string+"\n"
    
    print(speak_response)
    print(card_response)
    return statement("Contest Details:", speak_response, card_response)


def all_site_intent(event, context):
    data  = get_all_site_data(1)
    if(len(data)) == 0:
        speak_response = "There is no contest available now on any website."
        card_response = speak_response
    else:
        site = data[0][3].title()
        contest_name = data[0][0]
        startdate_string =  data[0][1].strftime('%B %d, %Y, %I %M %p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I %M %p')
        speak_response = "The next contest is on "+site+" and it is <prosody volume='x-loud' rate='slow'>"\
                    + contest_name +"</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> "\
                    + enddate_string + ", <say-as interpret-as='cardinal'>"+endtime_string+"</say-as>"
        card_response = "Site: "+ site +"\n"+\
                        "Contest: "+ contest_name +"\n"+\
                        "Start Time: "+ startdate_string +"\n"+\
                        "End Time: " + enddate_string + ", "+ endtime_string
    
    print(speak_response)
    print(card_response)
    return statement("Contest Details:", speak_response, card_response)

def single_site_all_contest_intent(event, context):
    site = event['request']['intent']['slots']['site']['value']
    print("You have selected "+site+" website")

    if (site in sites_available) == False:
        speak_response = "Sorry, didn't recognize the website name. Please try again."
        return statement("Contest Details:", speak_response)

    data  = get_site_data(site, 5)
    site = site.title()
    
    if(len(data)) == 0:
        speak_response = "There is no contest available now on "+ site
    else:
        speak_response = "The next 5 contests on "+ site \
                            +" are <prosody volume='x-loud' rate='slow'>"
        card_response = "Site: "+ site +"\n"

        for contest in data:
            contest_name = contest[0]
            startdate_string =  contest[1].strftime('%B %d, %Y, %I %M %p')
            enddate_string = contest[2].strftime('%B %d, %Y')
            endtime_string = contest[2].strftime('%I %M %p')
            speak_response += contest_name +", "
            
            card_response += "Contest: "+ contest_name +"\n"+\
                                "Start Time: "+ startdate_string +"\n"+\
                                "End Time: " + enddate_string + ", "+ endtime_string + "\n"
        
        speak_response += '</prosody>'

    print(speak_response)
    print(card_response)
    return statement("Contest Details:", speak_response, card_response)

##############################
# Required Intents
##############################


def cancel_intent():
    return statement("Cancel Request", "Ok. Canceled the request.")  #don't use CancelIntent as title it causes code reference error during certification 


def help_intent():
    response = "We can give you the current and future contests from different websites. "+\
                "We have currently enlisted: Codeforces, Codechef, Spoj, Hackerrank and Topcoder contests. "+\
                "For example: You can say like this: " +\
                "Ask Contest Reminder what is the next contest? "+\
                "or Ask Contest Reminder what is the next contest on website?"
    return statement("Help Information", response)       #same here don't use CancelIntent


def stop_intent():
    return statement("Stop Request", "Ok. Stopped the request.")      #here also don't use StopIntent


##############################
# On Launch
##############################


def on_launch(event, context):
    response = "Welcome from Contest Reminder. Ask me about the contests."
    return statement("Contest Reminder", response)

def on_error(event, context):
    response = "Sorry. We couldn't recognize your request. Please try again with a valid request."
    return statement("Contest Reminder", response)


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

        fetched_data.append([item['name'],startdate, enddate, item['website']])

    fetched_data = sorted(fetched_data, key=lambda x: x[2], reverse=False)
    # pprint(fetched_data)

    if(len(fetched_data) == 0):
        return []

    if(len(fetched_data) < count):
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

    if(len(fetched_data) == 0):
        return []

    if(len(fetched_data) < count):
        return fetched_data

    return fetched_data[:count]



