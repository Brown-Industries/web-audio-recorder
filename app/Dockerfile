FROM python:3.8-buster
RUN apt-get install bash
RUN apt-get update && apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 pulseaudio alsa-utils ffmpeg -y
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src /src
EXPOSE 5000
CMD python server.py
