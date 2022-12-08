FROM python:3.10
RUN mkdir -p /usr/src/bot1
WORKDIR /usr/src/bot1
COPY . /usr/src/bot1
RUN pip install -r requirements.txt
CMD ["python", "bot/bot_main.py"]
