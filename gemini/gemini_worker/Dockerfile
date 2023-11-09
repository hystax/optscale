FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY gemini/gemini_worker/requirements.txt gemini/gemini_worker/requirements.txt
RUN pip install --no-cache-dir -r gemini/gemini_worker/requirements.txt

COPY gemini/gemini_worker/*.py gemini/gemini_worker/
COPY gemini/gemini_worker/duplicate_object_finder gemini/gemini_worker/duplicate_object_finder
COPY gemini/gemini_worker/migrations gemini/gemini_worker/migrations

CMD ["python", "-u","/usr/src/app/gemini/gemini_worker/main.py"]
