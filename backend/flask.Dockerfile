# Use an official Python runtime as a parent image
FROM python:3.7-slim-buster
RUN apt-get update
RUN apt-get install gcc -y
# Set the working directory to /app

# Copy the current directory contents into the container at /debtstar
RUN mkdir ./debtstar
COPY ./requirements.txt ./requirements.txt
COPY ./app/server.py ./debtstar/server.py
RUN pip3 install -r requirements.txt

WORKDIR /debtstar
# RUN pip3 install requirements.txt
# Install any needed packages specified in requirements.txt
# RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "server.py"]
