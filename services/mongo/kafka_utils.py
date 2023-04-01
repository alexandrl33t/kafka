from kafka import KafkaConsumer
import time

def try_connect(server):
    try:
        return KafkaConsumer(bootstrap_servers=server)
    except Exception:
        return None

def get_kafka(server):
    for trying in range(40):
        conn = try_connect(server)
        if conn is not None:
            break

        time.sleep(0.5)
        
    return conn