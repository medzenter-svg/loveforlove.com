FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        scribus \
        ghostscript \
        poppler-utils \
        libimage-exiftool-perl \
        xvfb \
        xauth \
        fonts-dejavu-core \
        fontconfig \
        icc-profiles-free \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/store

COPY store /app/store
COPY products /app/products

RUN fc-cache -f \
    && python3 prepress/check_environment.py

# Approved premium fonts and the final production ICC/output-intent profiles
# are collection assets/configuration and must be supplied before release QA.
# The image deliberately does not download arbitrary proprietary fonts.

CMD ["python3", "prepress/check_environment.py"]
