FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt amqp.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt
COPY ./refund_orchestrator.py ./invokes.py ./amqp_connection.py ./
CMD [ "python", "./refund_orchestrator.py" ]