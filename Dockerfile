FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Use an environment variable to switch between app and test mode
ARG MODE=app
ENV MODE=${MODE}

CMD ["sh", "-c", "if [ \"$MODE\" = \"test\" ]; then pytest tests/e2e/ -v; else python main.py; fi"]
