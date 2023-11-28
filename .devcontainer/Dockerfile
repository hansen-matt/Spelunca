FROM python:latest

# Python packages
COPY requirements.txt /tmp/
COPY requirements_dev.txt /tmp/

RUN pip install --no-cache \
    -r /tmp/requirements.txt && \
    pip install --no-cache \
    -r /tmp/requirements_dev.txt