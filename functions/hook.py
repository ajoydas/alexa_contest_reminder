import json
from functions.fetch_data import sites_available, get_site_data, get_all_site_data
from functions.helpers import pp_json

source = 'google'


def endpoint(event, context):
    body = event['body']
    print(body)

    body = json.loads(body)

    action = body['queryResult']['action']
    global source
    source = body['originalDetectIntentRequest']['source']

    print(action)

    if action == 'input.single_site_intent':
        response_body = single_site_intent(body)

    elif action == 'input.all_site_intent':
        response_body = all_site_intent(body)

    elif action == 'input.single_site_all_intent':
        response_body = single_site_all_contest_intent(body)

    else:
        audio_res = "Welcome to Contest Reminder. How can I help you?"
        text_res = audio_res
        response_body = build_response(text_res, audio_res)

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response_body
    }

    pp_json(response)
    return response


def single_site_intent(body):
    site = body['queryResult']['parameters']['site']
    if site == "" or site is None or not(site in sites_available):
        audio_res = "Select one of the following websites"
        text_res = audio_res
        return build_response(text_res, audio_res, sites_available)

    data = get_site_data(site, 1)
    site = site.title()

    if (len(data)) == 0:
        speak_response = "There is no contest available now on " + site
        card_response = speak_response
    else:
        contest_name = data[0][0]
        startdate_string = data[0][1].strftime('%B %d, %Y, %I %M %p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I:%M%p')
        speak_response = "The next contest on " + site + " is <prosody volume='x-loud' rate='medium'>" \
                         + contest_name + "</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> " \
                         + enddate_string + ", <say-as interpret-as='time' format='hms12'>" + endtime_string + "</say-as>"
        card_response = "Site: " + site + "\n" + \
                        "Contest: " + contest_name + "\n" + \
                        "Start Time: " + startdate_string + "\n" + \
                        "End Time: " + enddate_string + ", " + endtime_string + "\n"

    print(speak_response)
    print(card_response)

    return build_response(card_response, speak_response)


def all_site_intent(body):
    data = get_all_site_data(1)
    if (len(data)) == 0:
        speak_response = "There is no contest available now on any website."
        card_response = speak_response
    else:
        site = data[0][3].title()
        contest_name = data[0][0]
        startdate_string = data[0][1].strftime('%B %d, %Y, %I %M %p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I:%M%p')
        speak_response = "The next contest is on " + site + " and it is <prosody volume='x-loud' rate='medium'>" \
                         + contest_name + "</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> " \
                         + enddate_string + ", <say-as interpret-as='time' format='hms12'>" + endtime_string + "</say-as>"
        card_response = "Site: " + site + "\n" + \
                        "Contest: " + contest_name + "\n" + \
                        "Start: " + startdate_string + "\n" + \
                        "End: " + enddate_string + ", " + endtime_string

    print(speak_response)
    print(card_response)
    return build_response(card_response, speak_response)


def single_site_all_contest_intent(body):
    site = body['queryResult']['parameters']['site']
    print("You have selected " + site + " website")

    if site == "" or site is None:
        audio_res = "Select one of the following websites"
        text_res = audio_res
        return build_response(text_res, audio_res, sites_available)

    data = get_site_data(site, 5)
    site = site.title()

    if (len(data)) == 0:
        speak_response = "There is no contest available now on " + site
        card_response = speak_response
    else:
        speak_response = "The next " + str(len(data)) + " contests on " + site \
                         + " are <prosody volume='x-loud' rate='medium'>"
        card_response = "Site: " + site + "\n"

        for contest in data:
            contest_name = contest[0]
            startdate_string = contest[1].strftime('%B %d, %Y, %I %M %p')
            enddate_string = contest[2].strftime('%B %d, %Y')
            endtime_string = contest[2].strftime('%I %M %p')
            speak_response += contest_name + ", "

            card_response += "Contest: " + contest_name + "\n" + \
                             "Start: " + startdate_string + "\n" + \
                             "End: " + enddate_string + ", " + endtime_string + "\n\n"

        speak_response += '</prosody>'

    print(speak_response)
    print(card_response)
    return build_response(card_response, speak_response)




def build_response(text_res, audio_res="", suggestion_res=[]):
    print(source)
    if source == 'facebook':
        return build_response_for_facebook(text_res, suggestion_res)
    else:
        return build_response_for_google(audio_res, text_res, suggestion_res)


def build_response_for_google(audio_res, text_res, suggestion_res=[]):
    simple_response = ""
    suggestions = ""

    if audio_res != "" or (text_res != "" and text_res is not None):
        simple_response = build_simpleResponse(audio_res, text_res)

    if suggestion_res is not None and len(suggestion_res) != 0:
        suggestions = build_suggestions(suggestion_res)

    response = '''
    {
    '''
    response += '"fulfillmentText": "' + text_res + '"'
    response += ''',
    "fulfillmentMessages": [{
        "simpleResponses": {

        }
    }],
    "payload": {
        "google": {
            "expectUserResponse": true,
            "richResponse": {
                "items": ['''

    if simple_response != "":
        response += simple_response

    response += " ] "
    if suggestions != "":
        if simple_response != "":
            response += ","
        response += suggestions
    response += '''
            }

        }
    }
    }
    '''

    return response


def build_response_for_facebook(text_res, suggestion_res=[]):
    print("Building response for facebook")

    suggestions = ""

    if suggestion_res is not None and len(suggestion_res) != 0:
        suggestions = build_suggestions_fb(suggestion_res)

    response = '''
        {
    '''
    response += '"fulfillmentText": "' + text_res + '"'
    response += ''',
    "fulfillmentMessages": [{
        "simpleResponses": {

        }
    }],
    "payload": {
        "facebook": { 
'''
    response += '"text": "' + text_res + '"'

    if suggestions != "":
        response += ","
        response += suggestions

    response += '''
      }

     }
    }
    '''

    return response


# "facebook": {
#          "text": "Pick a color:",
#          "quick_replies": [
#             {
#               "content_type": "text",
#               "title": "Red",
#               "payload": "red"
#             },
#             {
#               "content_type": "text",
#               "title": "Green",
#               "payload": "green"
#             }
#          ]
#       }

def build_simpleResponse(audio_res, text_res):
    response = '''{
            "simpleResponse": {  '''
    response += '"ssml": "<speak>' + audio_res + '</speak>"'
    response += '''
            }
        }'''

    return response


def build_suggestions(suggestion_res):
    response = '''
        "suggestions": [
    '''

    for indx, suggestion in enumerate(suggestion_res):
        response += '{ "title": "' + suggestion.title() + '"}'
        if (indx != len(suggestion_res) - 1):
            response += ","

    response += '''
            ]
        '''

    return response


def build_suggestions_fb(suggestion_res):
    response = '''
        "quick_replies": [
    '''

    for indx, suggestion in enumerate(suggestion_res):
        response += ''' {
            "content_type": "text",
        '''
        response += ' "title": "' + suggestion.title() + '" ,'

        response += ' "payload": "' + suggestion + '"'

        response += " } "
        if indx != len(suggestion_res) - 1:
            response += ","

    response += '''
            ]
        '''

    return response
