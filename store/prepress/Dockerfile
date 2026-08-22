FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LF_RGB_PROFILE_NAME="sRGB display profile (ICC v2.2)" \
    LF_CMYK_PROFILE_NAME="ISO Coated v2 300% (basICColor)" \
    LF_OUTPUT_PROFILE_NAME="ISO Coated v2 300% (basICColor)" \
    LF_TITLE_FONT="EB Garamond 12 Regular" \
    LF_BODY_FONT="Lato Regular"

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
        fonts-ebgaramond \
        fonts-lato \
        fontconfig \
        icc-profiles-free \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/store

COPY store /app/store
COPY products /app/products

RUN fc-cache -f \
    && fc-match "EB Garamond 12" \
    && fc-match "Lato" \
    && python3 prepress/check_environment.py

# EB Garamond and Lato are reproducible open-font-license dependencies available
# from Ubuntu 24.04. Both cover the active Latin/Greek/Cyrillic language set.
# Proprietary fonts are never downloaded automatically.
#
# The ICC defaults are reproducible release-baseline profiles. A receiving
# printer's exact paper/press output intent can replace LF_OUTPUT_PROFILE_NAME for
# a specific production run without changing collection layout or customer data.

CMD ["python3", "prepress/check_environment.py", "--require-profiles"]
