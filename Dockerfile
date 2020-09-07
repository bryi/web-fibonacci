FROM python:3.8-slim AS compile-image

RUN apt-get update \
&& apt-get install -y --no-install-recommends python3-dev gcc postgresql-client libpq-dev \
&& pip3 install --upgrade pip \
&& apt-get clean autoclean \
&& apt-get autoremove --yes \
&& rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY requirements.txt .

RUN pip3 install --user -r requirements.txt

FROM python:3.8-slim AS build-image

RUN mkdir app

COPY --from=compile-image /root/.local /root/.local

WORKDIR app/

COPY . .