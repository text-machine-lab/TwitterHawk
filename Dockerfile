FROM java:openjdk-8-jre
MAINTAINER Alexey Romanov <aromanov@cs.uml.edu>

EXPOSE 80

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python-numpy python-scipy python-dev python-pip python-nose python-enchant g++ libopenblas-dev git curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /usr/src/app
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn bottle # for REST API

COPY . /usr/src/app

RUN curl -SL https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/ark-tweet-nlp/ark-tweet-nlp-0.3.2.tgz \
    | tar -xzC /usr/src/app/tools/
RUN git clone https://github.com/ianozsvald/ark-tweet-nlp-python.git /usr/src/app/tools/ark-tweet-nlp-python
RUN cp /usr/src/app/tools/ark-tweet-nlp-python/CMUTweetTagger.py /usr/src/app/tools/ark-tweet-nlp-0.3.2/

CMD ["gunicorn", "--timeout", "120", "-b", "0.0.0.0:80", "twitter_hawk_api_server:app"]

