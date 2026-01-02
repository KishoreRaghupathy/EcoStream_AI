import json
import os
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')

class KafkaClient:
    @staticmethod
    def get_producer():
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logger.info("Kafka Producer initialized successfully")
            return producer
        except Exception as e:
            logger.error(f"Failed to initialize Kafka Producer: {e}")
            raise

    @staticmethod
    def get_consumer(topic, group_id='ecostream-group'):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=group_id,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(f"Kafka Consumer initialized for topic {topic}")
            return consumer
        except Exception as e:
            logger.error(f"Failed to initialize Kafka Consumer: {e}")
            raise
