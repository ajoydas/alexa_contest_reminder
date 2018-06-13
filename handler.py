##############################
# Builders
##############################


def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
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


def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
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

    if intent == "SingleWebsiteSingleContestIntent":
        return single_site_single_contest_intent(event, context)

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
    res = "You have selected "+site+" website"
    return statement("single_site_intent", res)


##############################
# Required Intents
##############################


def cancel_intent():
    return statement("CancelIntent", "You want to cancel")  #don't use CancelIntent as title it causes code reference error during certification 


def help_intent():
    return statement("CancelIntent", "You want help")       #same here don't use CancelIntent


def stop_intent():
    return statement("StopIntent", "You want to stop")      #here also don't use StopIntent


##############################
# On Launch
##############################


def on_launch(event, context):
    return statement("title", "body")
