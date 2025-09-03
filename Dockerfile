FROM python:latest
WORKDIR /app
COPY redirect.py /redirect.py
COPY install.sh /install.sh
RUN pip install --no-cache-dir requests environs
RUN chmod +x /redirect.py /install.sh
ENTRYPOINT ["/bin/sh", "/install.sh"]
