FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt amqp.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt
COPY ./app.py ./invokes.py ./amqp_connection.py ./
COPY ./templates/ ./templates/ 
COPY ./static/ ./static/
CMD [ "python", "./app.py" ]