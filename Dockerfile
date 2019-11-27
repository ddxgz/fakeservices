# FROM python:3.7-alpine
FROM ddxgz/datasci:1.0
WORKDIR /code
# RUN apk add --no-cache gcc musl-dev linux-headers make automake gcc g++ subversion python3-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .