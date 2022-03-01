# syntax=docker/dockerfile:1

FROM python:3.8

WORKDIR /app

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

#RUN unzip /tmp/chromedriver.zip chromedriver -d /app/

#install chrome driver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver





# Set display port as an environment variable
ENV DISPLAY :20.0
ENV SCREEN_GEOMETRY "1440x900x24"
ENV CHROMEDRIVER_PORT 4444
ENV CHROMEDRIVER_WHITELISTED_IPS "127.0.0.1"
ENV CHROMEDRIVER_URL_BASE ''
ENV CHROMEDRIVER_EXTRA_ARGS ''

EXPOSE 4444


COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY spree_spray.py ../scr/spray.py

RUN chmod 777 ../scr/spray.py

ENTRYPOINT ["python3","../scr/spray.py"]
