import os

from flask import Flask, request
import postgre_utils as utils
import postgre_create as create_utils
import logging
import datetime
import requests
import json
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

postgre = None

def comma_separated_params_to_list(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val)
    return result

def is_scheme_created(postgre):
    postgre.execute("SELECT * FROM information_schema.tables WHERE table_name = 'groups';")
    records = postgre.fetchall()

    if records:
        return True
    else:
        return False

def prepare_database(postgre):
    app.logger.info("Creating scheme")
    create_utils.create_scheme(postgre)
    app.logger.info("Created scheme")

    app.logger.info("Filling database")
    create_utils.fill_scheme(postgre)
    app.logger.info("Filled database")

@app.route("/api/students", methods=["GET"])
def get_students():
    args = request.args
    if "from" in args and "until" in args and "lessons" in args:
        app.logger.info("Search request")

        lections = args.getlist("lessons")
        if len(lections) == 1 and ',' in lections[0]:
            lections = tuple(comma_separated_params_to_list(lections[0]))

        start_date = datetime.datetime.strptime(args.get("from"), "%d-%m-%Y")
        end_date = datetime.datetime.strptime(args.get("until"), "%d-%m-%Y")

        app.logger.info(f"lessons = {lections}")
        app.logger.info(f"from = {start_date}")
        app.logger.info(f"until = {end_date}")

        return utils.find_worst_students(postgre, lections, start_date, end_date)

    return utils.get_students(postgre)

@app.route("/api/groups", methods=["GET"])
def get_groups():
    return utils.get_groups(postgre)

@app.route("/api/lessons", methods=["GET"])
def get_lessons():
    return utils.get_lessons(postgre)

@app.route("/api/courses", methods=["GET"])
def get_courses():
    groupsToCourses = utils.get_group_to_course(postgre)
    mappedGroups = dict()

    for groupToCourse in groupsToCourses:
        group = groupToCourse["group_fk"]
        course = groupToCourse["course_fk"]
        if course not in mappedGroups:
            mappedGroups[course] = []
        mappedGroups[course].append(group)

    res = []
    for key, val in mappedGroups.items():
        res.append({"name": key, "groups": val})

    return res
@app.route("/api/fill-database", methods=["GET"])
def fill_database():
    prepare_database(postgre)
    return "Mger"

def try_fetch(url):
    while True:
        app.logger.info(f"Fetching {url} ...")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                app.logger.info(f"Fetching {url} successded!")
                return response
        except Exception:
            app.logger.info(f"Fetching {url} failed")
        time.sleep(0.5)

if __name__ == "__main__":
    app.logger.info("Connecting to postgres")
    postgre = utils.get_postgre()
    app.logger.info("Connected to postgres")
    # fill_database()
    app.run(host="0.0.0.0", port=os.environ["LOCAL_SERVICES_PORT"])