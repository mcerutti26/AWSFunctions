import os
from AWSHelper import get_aws_parameter
from slack_sdk import WebClient
import json


class BussedSlackEvent:
    def __init__(self, raw_event):
        # Parse the raw event payload as it is received after being bussed from one AWS StepFunction to another
        self.content = raw_event
        # Messages have an ending quote that throws off json loading
        # Other payloads do not have this quote
        if raw_event['detail']['input'][-1] == "\"":
            self.body = json.loads(raw_event['detail']['input'][0:-1])
        else:
            self.body = json.loads(raw_event['detail']['input'])
        self.event_type = self.body.get('type')
        if self.event_type == 'view_submission':
            self.trigger_type = "modalSubmitted"
        else:
            self.trigger_type = "loadHome"
        self.body['trigger_type'] = self.trigger_type


class StateFunctionSlackEvent:
    # Parse the raw event payload as it is received after being passed from one Lambda to another within a StepFunction
    def __init__(self, raw_event):
        self.content = raw_event
        self.slack_token = get_aws_parameter(param_name=os.environ['slackBotTokenPath'])
        self.body = raw_event
        self.client = WebClient(token=self.slack_token)
        self.event_type = self.body.get('type')
        self._user_id = None
        self._human_trigger = None
        self._channel_id = None
        self._trigger_id = None
        self._button_type = None
        self._files = None
        self._n_strains = None
        self._n_plasmids = None
        self._un = None
        self._pw = None
        self._example_info = None
        self._src_lib = None

    @property
    def user_id(self):
        if self._user_id is None:
            if self.event_type == 'block_actions':
                self._user_id = self.body['user']['id']
            elif self.event_type == 'event_callback':
                self._user_id = self.body['event'].get('user')
            elif self.event_type == 'view_submission':
                self._user_id = self.body['user']['id']
            else:
                print('Error no body type match')
                return
        return self._user_id

    @property
    def human_trigger(self):
        if self._human_trigger is None:
            if self.event_type == 'block_actions':
                buttontype = self.body['actions'][0]['text']['text']
                self._human_trigger = buttontype.replace(' ', '').lower() + 'Clicked'
            elif self.event_type == 'event_callback':
                event_callback_type = self.body['event']['type']
                if event_callback_type == 'message':
                    self._human_trigger = 'messageReceived'
                elif 'opened' in event_callback_type:
                    tabtype = self.body['event'].get('tab')
                    self._human_trigger = tabtype + 'Opened'
                else:
                    self._human_trigger = 'unknownMessageOrTab'
            elif self.event_type == 'view_submission':
                buttontype = self.body['view']['title']['text']
                self._human_trigger = buttontype.replace(' ', '').lower() + 'Submitted'
            else:
                print('Error no body type match')
                return
            print(self._human_trigger)
        return self._human_trigger

    @property
    def channel_id(self):
        if self._channel_id is None:
            chat = self.client.conversations_open(users=self.user_id)
            self._channel_id = chat.data['channel']['id']
        return self._channel_id

    @property
    def trigger_id(self):
        if self._trigger_id is None:
            try:
                self._trigger_id = self.body['trigger_id']
            except KeyError:
                self._trigger_id = None
        return self._trigger_id

    @property
    def files(self):
        if self._files is None:
            try:
                self._files = self.body['event']['files']
            except KeyError:
                self._files = None
        return self._files

    @property
    def un_pw(self):
        if self._un is None and self._pw is None:
            # What was the username and password entered?
            usernameblockid = self.body['view']['blocks'][0]['block_id']
            self._un = self.body['view']['state']['values'][usernameblockid]['input_username'][
                'value']
            passwordblockid = self.body['view']['blocks'][1]['block_id']
            self._pw = self.body['view']['state']['values'][passwordblockid]['input_password'][
                'value']
        return self._un, self._pw
