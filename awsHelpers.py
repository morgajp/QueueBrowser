import boto3
from os.path import expanduser


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.sessions['default'] = boto3.Session()
        self.FillSessions()

    def FillSessions(self):
        defSess = self.sessions['default']
        for profile in defSess._session.available_profiles:
            self.sessions[profile] = boto3.Session(profile_name=profile)



class QueueManager:
    def __init__(self):
        self.sm = SessionManager()
        self.qmap = {}
        self.queues = []

    def getQueues(self):
        for s in self.sm.sessions.values(): 
            sqs = s.resource('sqs')
            sessionQueues = []

            try:
                for q in sqs.queues.all():
                    sessionQueues.append({'url': q.url, 
                                   'msgCount': q.attributes['ApproximateNumberOfMessages'],
                                   'ts': q.attributes['LastModifiedTimestamp'],
                                   'session': s})
            except:
                pass

            s.queues = sessionQueues
            self.queues.extend(sessionQueues)

        return self.queues


    def getMessages(self, QueueData):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        msgs = queue.receive_messages(VisibilityTimeout=20, MaxNumberOfMessages=10)

        QueueData['msgs'] = msgs

        return msgs


    def write(self, QueueData, text):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        queue.send_message(MessageBody=text)


    def purge(self, QueueData):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(queueUrl)
        queue.purge()

