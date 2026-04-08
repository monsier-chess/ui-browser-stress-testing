FROM python:3.10-slim
WORKDIR /app
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com
RUN pip install flask
COPY app.py .
CMD ["python", "app.py"]