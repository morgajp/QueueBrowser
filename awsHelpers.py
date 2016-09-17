import boto3


class QueueManager:
    def __init__(self):
        self.session = boto3.Session()
        self.qmap = {}

    def getQueues(self):
        sqs = self.session.resource('sqs')
        queues = []
        for q in sqs.queues.all():
            queues.append({'url': q.url, 
                           'msgCount': q.attributes['ApproximateNumberOfMessages'],
                           'ts': q.attributes['LastModifiedTimestamp']})

        self.queues = queues
        return queues


    def getMessages(self, QueueData):
        sqs = self.session.resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        msgs = queue.receive_messages(VisibilityTimeout=20, MaxNumberOfMessages=10)

        QueueData['msgs'] = msgs

        return msgs


    def write(self, QueueData, text):
        sqs = self.session.resource('sqs')
        queue = sqs.Queue(QueueData['url'])
        queue.send_message(MessageBody=text)


    def purge(self, queueUrl):
        sqs = self.session.resource('sqs')
        queue = sqs.Queue(queueUrl)
        queue.purge()


