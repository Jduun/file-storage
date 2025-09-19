FROM python:3.10

WORKDIR /app
RUN apt update && apt install

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
CMD ["uwsgi", "--ini", "uwsgi.ini"]
# CMD ["python", "src/app.py"]