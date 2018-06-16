import json
from functions.fetch_data import sites_available, get_site_data, get_all_site_data, links_parsed
from functions.helpers import pp_json

site = ''
source = 'google'
screen_capability = False


def endpoint(event, context):
    body = event['body']
    print(body)

    body = json.loads(body)

    action = body['queryResult']['action']
    global source
    source = body['originalDetectIntentRequest']['source']
    get_capability(body)

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

def get_capability(body):
    global screen_capability
    try:
        capabilities = body['originalDetectIntentRequest']['payload']['surface']['capabilities']
        for capability in capabilities:
            # print(capability['name'])
            if capability['name'] == 'actions.capability.SCREEN_OUTPUT':
                screen_capability = True
    except:
        pass
    print(screen_capability)


def single_site_intent(body):
    global site
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
        startdate_string = data[0][1].strftime('%B %d, %Y, %I:%M%p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I:%M%p')
        speak_response = "The next contest on " + site + " is <prosody volume='x-loud' rate='medium'>" \
                         + contest_name + "</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> " \
                         + enddate_string + ", <say-as interpret-as='time' format='hms12'>" + endtime_string + "</say-as>"
        card_response = "Site: " + site + "  \n" + \
                        "Contest: " + contest_name + "  \n" + \
                        "Start: " + startdate_string + "  \n" + \
                        "End: " + enddate_string + ", " + endtime_string + "  \n"

    print(speak_response)
    print(card_response)

    return build_response(card_response, speak_response)


def all_site_intent(body):
    global site
    data = get_all_site_data(1)
    if (len(data)) == 0:
        speak_response = "There is no contest available now on any website."
        card_response = speak_response
    else:
        site = data[0][3].title()
        contest_name = data[0][0]
        startdate_string = data[0][1].strftime('%B %d, %Y, %I:%M%p')
        enddate_string = data[0][2].strftime('%B %d, %Y')
        endtime_string = data[0][2].strftime('%I:%M%p')
        speak_response = "The next contest is on " + site + " and it is <prosody volume='x-loud' rate='medium'>" \
                         + contest_name + "</prosody> and it will end on <say-as interpret-as='spell-out'>UTC</say-as> " \
                         + enddate_string + ", <say-as interpret-as='time' format='hms12'>" + endtime_string + "</say-as>"
        card_response = "Site: " + site + "  \n" + \
                        "Contest: " + contest_name + "  \n" + \
                        "Start: " + startdate_string + "  \n" + \
                        "End: " + enddate_string + ", " + endtime_string

    print(speak_response)
    print(card_response)
    return build_response(card_response, speak_response)


def single_site_all_contest_intent(body):
    global site
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

        card_response = "Site: " + site + "  \n"

        for contest in data:
            contest_name = contest[0]
            startdate_string = contest[1].strftime('%B %d, %Y, %I:%M%p')
            enddate_string = contest[2].strftime('%B %d, %Y')
            endtime_string = contest[2].strftime('%I:%M%p')
            speak_response += contest_name + ", "

            if source == 'google':
                card_response += "**Contest: " + contest_name + "**  \n" + \
                                 "Start: " + startdate_string + "  \n" + \
                                 "End: " + enddate_string + ", " + endtime_string + "  \n"
            else:
                card_response += "Contest: " + contest_name + "  \n" + \
                                 "Start: " + startdate_string + "  \n" + \
                                 "End: " + enddate_string + ", " + endtime_string + "  \n  \n"

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
    card_response = ""
    suggestions = ""

    if audio_res != "":
        simple_response = build_simpleResponse(audio_res, text_res)

    if screen_capability and text_res != "" and text_res is not None:
        card_response = build_cardRespone(text_res)

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

    if card_response != "":
        if simple_response != "":
            response += ","
        response += card_response

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
    global site
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

    if suggestions != "":
        response += '"text": "' + text_res + '"'

        response += ","
        response += suggestions

    else:
        response += '''
         "attachment": {
          "type":"template",
          "payload":{
            "template_type":"button", '''
        response += '"text": "' + text_res + '"'

        print(site)
        site = site.lower()
        if site != "" and (site in sites_available):
            response += ","
            response += ''' "buttons":[
                  {
                    "type":"web_url", '''
            response += '"url": "' + links_parsed[site] + '"'
            response += ''' ,
                    "title":"More Details"
                  }
                ]
                '''
    response +='''
          }
        }
        '''

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


def build_cardRespone(text_res):
    global site
    response = '''{
                "basicCard": {  '''

    response += '"title": "Details: ", '
    response += '"formattedText": "'+text_res + '"'

    print(site)
    site = site.lower()
    if site != "" and (site in sites_available):
        response += '''
        ,
        "buttons": [
            {
                "title": "More Details",
                "openUrlAction": {
        '''
        response += '"url": "'+ links_parsed[site] + '"'
        response += '''
                 }
            }
        ]
        '''

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
