import os
import psycopg2
import time

TABLE_INSTITUTES = "institutes"
TABLE_DEPARTMENTS = "departments"
TABLE_SPECIALITIES = "specialities"
TABLE_COURSES = "courses"

TABLE_STUDENTS = "students"
TABLE_GROUPS = "groups"
TABLE_VISITS = "visits"
TABLE_LESSONS = "lessons"
TABLE_SCHEDULE = "schedule"

def try_connect():
    try:
        return psycopg2.connect(dbname=os.environ["POSTGRE_DBNAME"], user=os.environ["POSTGRE_USER"], 
                        password=os.environ["POSTGRE_PASS"], host="postgres", connect_timeout=30)
    except Exception:
        return None

def get_postgre():
    for trying in range(20):
        conn = try_connect()
        if conn is not None:
            break

        time.sleep(0.5)
        
    conn.autocommit = True
    return conn.cursor()

def get_students(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_STUDENTS}")
    students = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return students

def get_groups(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_GROUPS}")
    groups = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return groups

def get_schedule(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_SCHEDULE}")
    schedule = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return schedule

def get_lessons(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_LESSONS}")
    lessons = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return lessons

def get_specialities(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_SPECIALITIES}")
    specialities = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return specialities

def get_courses(postgre):
    postgre.execute(f"SELECT * FROM {TABLE_COURSES}")
    courses = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return courses

def get_departments(postgre, name, inst):
    postgre.execute(f"SELECT * FROM {TABLE_DEPARTMENTS} WHERE name = '{name}' AND institute_fk = {inst}")
    departments = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return departments

def get_group_to_course(postgre):
    postgre.execute(f"SELECT group_fk, course_fk FROM {TABLE_SCHEDULE} JOIN {TABLE_LESSONS} ON {TABLE_SCHEDULE}.lesson_fk = {TABLE_LESSONS}.id GROUP BY group_fk, course_fk;")
    courses = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return courses

def find_worst_students(postgre, lections, start_date, end_date):
    postgre.execute(f"SELECT student_fk AS id, CAST(COUNT(CASE visited WHEN true THEN 1 ELSE NULL END) AS FLOAT) / COUNT(*) AS visit_percent \
                      FROM visits JOIN schedule ON visits.schedule_fk = schedule.id \
                      WHERE schedule.lesson_fk IN {lections} AND schedule.time BETWEEN '{start_date}' AND '{end_date}' \
                      GROUP BY student_fk \
                      ORDER BY visit_percent \
                      LIMIT 10;")

    students = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return students