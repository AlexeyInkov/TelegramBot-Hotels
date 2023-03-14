FROM python:3.11.2-alpine
RUN mkdir /usr/app
WORKDIR /usr/app
ENV PYTHONPATH /usr/app
COPY . .
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]


# docker run --name my_bot -d --rm --env [BOT_TOKEN=6160654985:AAEWyjhpKNTAqImxirYl3LnoNjkspalJx4c, RAPID_API_KEY=3c89c30747msh2965d14cb19bd65p10fb5cjsne1896a63ef78] mybot

