# Playwright runner of the e2e stack (browsers are in the base image).
# renovate: datasource=docker depName=mcr.microsoft.com/playwright/python
FROM mcr.microsoft.com/playwright/python:v1.65.2-noble
WORKDIR /e2e
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt
CMD ["pytest", "tests", "-v", "--tracing", "retain-on-failure", "--output", "results/playwright", "--junitxml", "results/junit.xml"]
