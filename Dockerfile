FROM python:3.7.3-alpine

WORKDIR /usr/src/app/

COPY requirements.txt requirements.txt
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && pip install gunicorn \
  && apk del build-dependencies

COPY application application
COPY migrations migrations
COPY main.py config.py boot.sh ./

RUN chmod +x boot.sh

ENV FLASK_APP main.py


EXPOSE 8181

ENTRYPOINT ["./boot.sh"]
