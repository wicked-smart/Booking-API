FROM surnet/alpine-wkhtmltopdf:3.18.0-0.12.6-small as wkhtmltopdf
FROM python:3.10-alpine

WORKDIR /app
# Install PostgreSQL client libraries and headers

COPY requirements.txt .

RUN \
    apk add --no-cache postgresql-libs  &&  \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip3 install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps 

# Install additional dependencies
RUN apk add --no-cache \
    build-base \
    libxslt-dev \
    libxml2-dev \
    libffi-dev \
    openssl-dev \
    curl \
    fontconfig \
    libstdc++ \
    freetype \
    ttf-droid \
    ttf-freefont \
    ttf-liberation

## Install libxrender package
RUN apk add --no-cache libxrender

# Copy wkhtmltopdf binary from the build stage to the final stage
COPY --from=wkhtmltopdf /bin/wkhtmltopdf /usr/bin/wkhtmltopdf


COPY . .


CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000
