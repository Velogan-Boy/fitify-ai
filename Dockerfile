# Use the Python3.7.2 image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
COPY . /app

RUN apt-get update
RUN apt-get install 'libgl1-mesa-dev' -y

# Install the dependencies
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]