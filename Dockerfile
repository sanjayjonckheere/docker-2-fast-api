FROM python:3

WORKDIR /app

RUN mkdir /db # Create db folder

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD uvicorn main:app --host 0.0.0.0 --port 8000