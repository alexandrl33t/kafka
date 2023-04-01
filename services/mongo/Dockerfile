FROM python:3.10.9-slim-bullseye

WORKDIR /app

#RUN apt-get update && apt-get -y install libpq-dev gcc

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]