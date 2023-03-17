FROM python:3.11.2-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "main.py" ]


# docker run --name my_bot -d --rm --] mybot

