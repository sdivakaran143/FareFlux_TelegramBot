
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN playwright install --with-deps

CMD ["python", "bot.py"]
