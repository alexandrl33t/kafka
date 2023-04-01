import mongo_utils as mongo
import kafka_utils as kafk

import os
import logging
import json
from kafka import KafkaConsumer
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

class InstitutesMessageProcessor:
    def process(self, mongo: MongoClient, message):
        operation = message['payload']['op']

        message = message['payload']

        if operation == "c":
            mongo.insert_one({"id": message["after"]["id"], "name": message["after"]["name"]})
        elif operation == "u":
            mongo.update_one({"id": message["after"]["id"]}, {"$set": {"name": message["after"]["name"]}})
        elif operation == "d":
            mongo.delete_one({"id": message["before"]["id"]})
        else:
            logging.info(f"Wrong operation type: {operation}, 'MGER' expected")

class DeparmentsMessageProcessor:
    def process(self, mongo: MongoClient, message):
        operation = message['payload']['op']

        message = message['payload']

        if operation == "c":
            mongo.update_one({"id": message["after"]["institute_fk"]}, 
                {"$push": {"departments": {"id": message["after"]["id"], "name": message["after"]["name"]}}})
        elif operation == "u":
            mongo.update_one({"departments.id": message["after"]["id"]}, 
                {"$set": {"departments.$[dep].name": message["after"]["name"]}},
                array_filters=[ {"dep.id": message["after"]["id"]}])
        elif operation == "d":
            mongo.update_one({"departments.id": message["before"]["id"]}, 
                {"$pull": {"departments": {"id": message["before"]["id"]}}})
        else:
            logging.info(f"Wrong operation type: {operation}, 'MGER' expected")

class SpecialitiesMessageProcessor:
    def process(self, mongo: MongoClient, message):
        operation = message['payload']['op']

        message = message['payload']

        if operation == "c":
            mongo.update_one({"departments.id": message["after"]["department_fk"]}, 
                {"$push": {"departments.$[dep].specs": {"id": message["after"]["id"], "name": message["after"]["name"]}}}, 
                array_filters= [ {"dep.id": message["after"]["department_fk"]}])
        elif operation == "u":
            mongo.update_one({"departments.specs.id": message["after"]["id"]}, 
                {"$set": {"departments.$.specs.$[spec].name": message["after"]["name"]}}, 
                array_filters= [ {"spec.id": message["after"]["id"]}])
        elif operation == "d":
            mongo.update_one({"departments.specs.id": message["before"]["id"]}, 
                {"$pull": {"departments.$.specs": {"id": message["before"]["id"]}}})
        else:
            logging.info(f"Wrong operation type: {operation}, 'MGER' expected")

class CoursesMessageProcessor:
    def process(self, mongo: MongoClient, message):
        operation = message['payload']['op']

        message = message['payload']

        if operation == "c":
            mongo.update_one({"departments.id": message["after"]["department_fk"]}, 
                {"$push": {"departments.$[dep].courses": {"id": message["after"]["id"], "name": message["after"]["name"]}}}, 
                array_filters= [ {"dep.id": message["after"]["department_fk"]}])
        elif operation == "u":
            mongo.update_one({"departments.courses.id": message["after"]["id"]}, 
                {"$set": {"departments.$.courses.$[crs].name": message["after"]["name"]}}, 
                array_filters= [ {"crs.id": message["after"]["id"]}])
        elif operation == "d":
            mongo.update_one({"departments.courses.id": message["before"]["id"]},
                {"$pull": {"departments.$.courses": {"id": message["before"]["id"]}}})
        else:
            logging.info(f"Wrong operation type: {operation}, 'MGER' expected")

class MessageProcessorFactory:
    def get_processor(self, topic):
        if topic == "postgres-sync.public.institutes":
            return InstitutesMessageProcessor()
        elif topic == "postgres-sync.public.departments":
            return DeparmentsMessageProcessor()
        elif topic == "postgres-sync.public.specialities":
            return SpecialitiesMessageProcessor()
        elif topic == "postgres-sync.public.courses":
            return CoursesMessageProcessor()
        else:
            raise ValueError(topic + ", Mger?")

if __name__ == "__main__":
    logging.info("Connecting to mongo...")
    mongo_client = mongo.get_mongo()
    logging.info("Connected to mongo")

    mongo_client = mongo_client["mirea"]["institutes"]

    server = os.getenv("KAFKA_ADDRESS", "broker:29092")
    logging.info(f"Connecting to kafka on '{server}' address")
    #consumer = kafk.get_kafka(server)
    consumer = KafkaConsumer(bootstrap_servers=server, group_id="mongo-sync-mgerector")
    logging.info("Connected to kafka")

    logging.info("Subscribing on topics...")
    consumer.subscribe(["postgres-sync.public.institutes", "postgres-sync.public.departments", "postgres-sync.public.specialities", "postgres-sync.public.courses"])
    logging.info("Subscribed on topics")

    for msg in consumer:
        topic = msg.topic
        body = json.loads(msg.value.decode())

        logging.info(f"Recieved message!")
        logging.info(f"Topic: {topic}")
        logging.info(f"Operation: {body['payload']['op']}")
        logging.info(f"Message body: {body['payload']}")

        factory = MessageProcessorFactory()
        processor = factory.get_processor(topic)
        processor.process(mongo_client, body)