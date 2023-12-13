FROM python:3.11
WORKDIR /based_bot
COPY requirements.txt /based_bot/
RUN pip install -r requirements.txt
COPY . /main
CMD python main.py
