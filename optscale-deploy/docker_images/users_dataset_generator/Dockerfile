FROM acura-dr.dts.loc/optscale_python:94098b67b949e2fabcc2404becf90a25f77496e6
MAINTAINER Hystax

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY users_dataset_generator.py .

CMD ["python", "/src/users_dataset_generator.py"]
