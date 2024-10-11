FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["python", "master.py"]
