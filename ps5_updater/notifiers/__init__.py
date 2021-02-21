from abc import ABC, abstractmethod
from decouple import config
import boto3


class Notifier(ABC):
    """base class for crawlers"""

    @abstractmethod
    def crawler_factory(self):
        pass

    def send_notification(self):
        """
        go to site's home page, select an
        area, then check out if item is in stock
        if it's in stock, then use sns to send a
        message
        """
        crawler = self.crawler_factory()
        crawler.find_ps5_page()
        status = crawler.get_status()
        if status:
            self.publish(crawler.store)
        return status

    def publish(self, store):
        """
        publish to email and phone
        """
        arn = config('ARN')
        region = config('AWS_REGION')
        client = boto3.client('sns', region_name=region)
        response = client.publish(TopicArn=arn, Message=f'Ps5 is in stock at {store}')
        return response


