FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY inas_cli ./inas_cli
COPY main.py ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["inas"]
CMD ["--help"]
