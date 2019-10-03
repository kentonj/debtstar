# Use an official Python runtime as a parent image
FROM python:3.7-slim-buster
RUN apt-get update
RUN apt-get install gcc -y
# Set the working directory to /app

RUN mkdir ./debtstar
COPY ./requirements.txt ./requirements.txt
COPY ./app/server.py ./debtstar/server.py
COPY ./debt-star-firebase-adminsdk-key.json ./debt-star-firebase-adminsdk-key.json
RUN pip3 install -r requirements.txt

WORKDIR /debtstar
# RUN pip3 install requirements.txt
# Install any needed packages specified in requirements.txt
# RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "server.py"]
