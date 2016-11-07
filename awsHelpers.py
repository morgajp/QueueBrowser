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
        self.sessionNodes = {}

    def getSessions(self):
        return self.sm.sessions.keys()

    def getQueues(self):
        for sname, s in self.sm.sessions.items(): 
            sqs = s.resource('sqs')
            sessionQueues = []

            try:
                for q in sqs.queues.all():
                    sessionQueues.append({'url': q.url, 
                       'msgCount': q.attributes['ApproximateNumberOfMessages'],
                       'ts': q.attributes['LastModifiedTimestamp'],
                       'awsobj': q,
                       'sessionname': sname,
                       'session': s})
            except:
                pass

            s.queues = sessionQueues
            self.queues.extend(sessionQueues)

        return self.queues

    def refresh(self, QueueData):
        awsq = QueueData['awsobj']
        awsq.load()
        newcount = awsq.attributes['ApproximateNumberOfMessages']
        newts = awsq.attributes['LastModifiedTimestamp']
        QueueData['msgCount'] = newcount
        QueueData['ts'] = newts


    def getMessages(self, QueueData):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        msgs = queue.receive_messages(VisibilityTimeout=20, 
                MaxNumberOfMessages=10,
                WaitTimeSeconds=2)

        QueueData['msgs'] = msgs

        return msgs

    def addByUrl(self, QueueData, Url):
        pass


    def write(self, QueueData, text):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        queue.send_message(MessageBody=text)


    def purge(self, QueueData):
        sqs = QueueData['session'].resource('sqs')
        queue = sqs.Queue(queueUrl)
        queue.purge()

