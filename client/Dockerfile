FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "secondary.py"]
