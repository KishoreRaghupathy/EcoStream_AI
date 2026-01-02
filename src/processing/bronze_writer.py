import os
import json
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from src.common.kafka_utils import KafkaClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = os.getenv('DATA_DIR', 'data/bronze')

class BronzeWriter:
    def __init__(self, topic):
        self.topic = topic
        self.consumer = KafkaClient.get_consumer(topic, group_id=f'bronze-writer-{topic}')
        self.batch_size = 100
        self.buffer = []

    def flush_buffer(self):
        if not self.buffer:
            return
        
        try:
            df = pd.DataFrame(self.buffer)
            # Add processing timestamp
            df['ingested_at'] = datetime.utcnow()
            
            # Create path
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            path = os.path.join(DATA_DIR, self.topic, f'date={date_str}')
            os.makedirs(path, exist_ok=True)
            
            filename = f"{int(time.time()*1000)}.parquet"
            full_path = os.path.join(path, filename)
            
            table = pa.Table.from_pandas(df)
            pq.write_table(table, full_path)
            
            logger.info(f"Written {len(df)} records to {full_path}")
            self.buffer = []
        except Exception as e:
            logger.error(f"Error writing batch: {e}")

    def run(self):
        logger.info(f"Starting Bronze Writer for {self.topic}...")
        try:
            for message in self.consumer:
                self.buffer.append(message.value)
                
                if len(self.buffer) >= self.batch_size:
                    self.flush_buffer()
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            self.flush_buffer()
            self.consumer.close()

if __name__ == "__main__":
    import threading

    def start_writer(topic):
        writer = BronzeWriter(topic)
        writer.run()

    # Run threads for both topics
    t1 = threading.Thread(target=start_writer, args=('weather-raw',))
    t2 = threading.Thread(target=start_writer, args=('airquality-raw',))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
