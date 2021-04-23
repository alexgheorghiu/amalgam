FROM ubuntu:20.04

# Setup up OS
RUN apt-get -y update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Setup application
ENV AMALGAM_SQLALCHEMY_DATABASE=sqlite
WORKDIR /app
COPY amalgam amalgam

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
EXPOSE 5000

CMD [ "python3", "-m" , "amalgam.app"]

# To build it: docker build -t amalgam .
# To run it as daemon: docker run -d -it -p 5000:5000 --name=amalgam amalgam
# To run it with open terminal: docker run -it -p 5000:5000 --name=amalgam amalgam
# To access it: http://localhost:5000

