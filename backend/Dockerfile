# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.11

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# [START cloudrun_system_package_ubuntu]
# [START run_system_package_ubuntu]
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y && apt-get clean
# [END run_system_package_ubuntu]
# [END cloudrun_system_package_ubuntu]

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec uvicorn --host 0.0.0.0 --port 8080 main:app
