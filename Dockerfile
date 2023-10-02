FROM python:3-alpine

RUN adduser -D nonroot && apk add --no-cache git
RUN mkdir /app/

WORKDIR /app
COPY . /app/

RUN pip install -r requirements.txt

# define the port number the container should expose
EXPOSE 5000

USER nonroot

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app" ]
