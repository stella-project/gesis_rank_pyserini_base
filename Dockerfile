FROM python:3.12-trixie

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jdk-headless && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --no-cache-dir \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "app.py"]
