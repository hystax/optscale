FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY gemini/gemini_scheduler/requirements.txt gemini/gemini_scheduler/requirements.txt
RUN pip install --no-cache-dir -r gemini/gemini_scheduler/requirements.txt
COPY gemini/gemini_scheduler/*.py ./gemini/gemini_scheduler/

CMD ["python", "-u","/usr/src/app/gemini/gemini_scheduler/main.py"]
