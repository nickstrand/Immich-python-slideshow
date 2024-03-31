FROM python:latest
ADD redirect.py /srv/redirect.py
RUN pip install requests environs
EXPOSE 8000
ENTRYPOINT [ "python3", "/srv/redirect.py" ]
