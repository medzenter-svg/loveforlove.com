FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LF_RGB_PROFILE_NAME="sRGB display profile (ICC v2.2)" \
    LF_CMYK_PROFILE_NAME="ISO Coated v2 300% (basICColor)" \
    LF_OUTPUT_PROFILE_NAME="ISO Coated v2 300% (basICColor)"

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

# These defaults are reproducible, openly distributable smoke/release-baseline
# profiles already available with Scribus/OpenICC packages. A receiving printer's
# exact paper/press output intent can replace LF_OUTPUT_PROFILE_NAME for a specific
# production run without changing the collection layout or customer data.
# Proprietary premium fonts are never downloaded automatically.

CMD ["python3", "prepress/check_environment.py", "--require-profiles"]
