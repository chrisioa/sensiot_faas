ARG IMAGE_TARGET=python:3.6-slim
ARG ARCH=amd64

FROM alpine AS qemu
ARG QEMU_VERSION=v2.12.0
ARG QEMU=x86_64
RUN echo ${QEMU}
ADD https://github.com/multiarch/qemu-user-static/releases/download/${QEMU_VERSION}/qemu-${QEMU}-static /qemu-${QEMU}-static
RUN chmod +x /qemu-${QEMU}-static

FROM ${ARCH}/${IMAGE_TARGET}
ARG QEMU=x86_64
COPY --from=qemu /qemu-${QEMU}-static /usr/bin/

WORKDIR /app
RUN echo "starting"
RUN apt-get clean && \
    apt-get update && \
    apt install -qqy --no-install-recommends \
    gcc build-essential python3-dev git && \
    git clone https://github.com/adafruit/Adafruit_Python_DHT.git && \
    cd Adafruit_Python_DHT && \
    python3 setup.py install --force-pi && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY src /app/
RUN chmod +x /app/manager.py

ENTRYPOINT ["/app/manager.py"]

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG VCS_URL
LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.vendor="Universitätsbibliothek Bamberg" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL
