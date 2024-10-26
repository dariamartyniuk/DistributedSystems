FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "if [ \"$PORT\" = \"5000\" ]; then python master.py; else python secondary.py; fi"]
