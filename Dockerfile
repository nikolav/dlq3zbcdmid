FROM python:3

WORKDIR /home/app

# requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt


# add chrome --headless for pdfs
RUN apt update; apt-get update -y
RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb


COPY . .

CMD [ "python", "api.py" ]
