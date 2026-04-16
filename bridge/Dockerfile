FROM python:3.9-slim
WORKDIR /app
RUN pip install requests
COPY detection-bridge.py .
CMD ["python", "-u", "detection-bridge.py"]
