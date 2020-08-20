# FROM postgres:latest
# RUN apt-get update && apt-get install -y python3 python3-pip
# COPY . /app
# WORKDIR /app
# RUN pip3 install --no-cache-dir -r requirements.txt
# EXPOSE 8080
# EXPOSE 5432
# CMD cd ./src && uvicorn main:app --reload --host 0.0.0.0 --port 8080

FROM tiangolo/uvicorn-gunicorn:python3.8
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
