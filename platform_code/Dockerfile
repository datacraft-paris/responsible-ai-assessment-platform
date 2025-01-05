# Pull official base image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set work directory
RUN mkdir code
WORKDIR /code

# Install system dependencies
RUN apk update && apk add --no-cache \
    postgresql-dev gcc python3-dev \
    musl-dev jpeg-dev zlib-dev libpq libjpeg

# Copy project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Make entrypoint.sh executable
RUN chmod +x ./entrypoint.sh

# Set entrypoint
ENTRYPOINT ["sh", "/code/entrypoint.sh"]
