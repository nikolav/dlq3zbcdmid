FROM python:3

WORKDIR /home/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# CMD [ "python", "api.py" ]
CMD [ "python", "-m", "flask", "--app", "api", "run", "--debug" ]



