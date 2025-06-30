ARG python_ver=3.12
FROM python:${python_ver}

ARG netbox_ver=master
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# -------------------------------------------------------------------------------------
# Install NetBox
# -------------------------------------------------------------------------------------
RUN git clone --single-branch --branch ${netbox_ver} https://github.com/netbox-community/netbox.git /opt/netbox/ && \
    cd /opt/netbox/ && \
    pip install -r /opt/netbox/requirements.txt

# RUN echo napalm >> /opt/netbox/local_requirements.txt && \
#     pip install -r /opt/netbox/local_requirements.txt

# Work around https://github.com/rq/django-rq/issues/421
#RUN pip install django-rq==2.3.2
#RUN pip install tzdata

# -------------------------------------------------------------------------------------
# Install Netbox Plugin
# -------------------------------------------------------------------------------------
RUN mkdir -p /source/plugsbox/plugsbox/
WORKDIR /source/plugsbox
COPY plugsbox /source/plugsbox/plugsbox/
COPY setup.py /source/plugsbox
COPY MANIFEST.in /source/plugsbox

#RUN pip install -r requirements.txt
RUN python setup.py develop

WORKDIR /opt/netbox/netbox/
