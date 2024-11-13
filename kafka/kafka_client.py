import uuid
from dataclasses import dataclass
from confluent_kafka import Consumer
import json

from os import getenv
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer

load_dotenv()

KAFKA_CLIENT_API_KEY = getenv("KAFKA_CLIENT_API_KEY")
KAFKA_CLIENT_API_SECRET = getenv("KAFKA_CLIENT_API_SECRET")
KAFKA_BOOTSTRAP_SERVER = getenv("KAFKA_CLIENT_BOOTSTRAP")


"""
This functionality is currently a POC and therefor, untested.  There are authorization issues currently blocking 
it's implementation, but it IS tested and working for local kubernetes/kafka setups.  
"""

@dataclass
class KafkaConsumerConfig:
    bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVER
    security_protocol = "SASL_SSL"
    sasl_mechanisms = "PLAIN"
    sasl_username: str = KAFKA_CLIENT_API_KEY
    sasl_password: str = KAFKA_CLIENT_API_SECRET
    session_timeout: int = 45000

    def get_config(self):
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
            "sasl.mechanism": self.sasl_mechanisms,
            "sasl.username": self.sasl_username,
            "sasl.password": self.sasl_password,
            "session.timeout.ms": self.session_timeout,
        }


class KafkaClientConfluent:
    def __init__(
            self,
            topic,
            group_id,
            records: [str],
            config: KafkaConsumerConfig = None,
            offset_reset: str = "latest"
    ):

        if config is None:
            conf = KafkaConsumerConfig()
            self.conf = conf.get_config()
            self.conf["group.id"] = group_id
            self.conf['auto.offset.reset'] = offset_reset
            self.consumer = Consumer(self.conf)
            self.topic = topic
            self.consumed_messages = 0
            self.records = records
            self.consumed_matching_records = []

        print(self.conf)

    def check_record(self, key):
        if key in self.records:
            return True
        else:
            return False

    def start_consumer(
            self,
            callback=None,
            callback_args=None
    ):
        """
        Starts a consumer based on the instance attributes of the KafkaClient class.

        :param callback:                    Reference to the function that needs to run after consumer is
                                            subscribed to the topic, typically to post an event.
        :param callback_args:               Argument to the referenced function
        :param callback_kwargs:             key word arguments to the referenced function
        :return:
        """
        self.consumer.subscribe([self.topic])

        total_count = 0
        number_of_records = len(self.records)

        if callback:
            callback(callback_args)

        try:
            while len(self.consumed_matching_records) < number_of_records:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    # No message available within timeout.
                    # Initial message consumption may take up to
                    # `session.timeout.ms` for the consumer group to
                    # rebalance and start consuming
                    print("Waiting for message or event/error in poll()")
                    continue
                elif msg.error():
                    print('error: {}'.format(msg.error()))
                else:
                    # Check for Kafka message
                    record_key = msg.key().decode("utf-8")
                    record_value = msg.value().decode("utf-8")
                    data = json.loads(record_value)
                    count = data['count']
                    total_count += count
                    print("Consumed record with key {} and value {}, \
                              and updated total count to {}"
                          .format(record_key, record_value, total_count))
                    key_string = json.loads(record_key)
                    match = self.check_record(key_string)
                    if match:
                        self.consumed_matching_records.append({key_string: data})
                    else:
                        continue
        except KeyboardInterrupt:
            pass
        self.consumer.close()


class KafkaClientStandardProducer(KafkaProducer):
    def __init__(
            self,
            bootstrap_server,
            security_protocol='PLAINTEXT',
            ssl_cafile=None,
            ssl_certfile=None,
            ssl_keyfile=None,
            ssl_password=None,
            sasl_mechanism=None,
            sasl_plain_username=None,
            sasl_plain_password=None,
            sasl_oauth_token_provider=None,
    ):
        super().__init__(
            bootstrap_servers=bootstrap_server,
            security_protocol=security_protocol,
            ssl_cafile=ssl_cafile,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile,
            ssl_password=ssl_password,
            sasl_mechanism=sasl_mechanism,
            sasl_plain_username=sasl_plain_username,
            sasl_plain_password=sasl_plain_password,
            sasl_oauth_token_provider=sasl_oauth_token_provider,
        )

    def produce(
            self,
            topic,
            data,
            key=str(uuid.uuid4())
    ):
        key = bytes(key, 'utf-8')
        data = bytes(json.dumps(data), "utf-8")
        if self.bootstrap_connected():
            future = self.send(topic, key=key, value=data)
            result = future.get(timeout=60)
            if result:
                print(f"Kafka producer successfully posted to {topic}, Result: {result}")
                return True
            else:
                print(f"Kafka producer failed to post to {topic} topic: {data},\n Result: {result}")
                return False
        else:
            print("Unable to connect to kafka bootstrap server")
            return False


class KafkaClientStandardConsumer(KafkaConsumer):
    def __init__(
            self,
            bootstrap_server,
            topics: list | dict = None,
            security_protocol='PLAINTEXT',
            ssl_cafile=None,
            ssl_certfile=None,
            ssl_keyfile=None,
            ssl_password=None,
            sasl_mechanism=None,
            sasl_plain_username=None,
            sasl_plain_password=None,
            sasl_oauth_token_provider=None,
    ):
        super().__init__(
            bootstrap_servers=bootstrap_server,
            group_id="QE_Test_Automation",
            security_protocol=security_protocol,
            ssl_cafile=ssl_cafile,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile,
            ssl_password=ssl_password,
            sasl_mechanism=sasl_mechanism,
            sasl_plain_username=sasl_plain_username,
            sasl_plain_password=sasl_plain_password,
            sasl_oauth_token_provider=sasl_oauth_token_provider,
            enable_auto_commit=False
        )
        self.topics = topics
        self.subscribe(self.topics)
        self.records = {}

    def get_messages(self, timeout_ms=60000, max_records=1000):
        messages = self._poll_once(timeout_ms=timeout_ms, max_records=max_records)
        return messages

    def get_message_by_key(self, key):
        messages = self.get_messages()
        return messages
        # TODO: Test format of messages to find key


