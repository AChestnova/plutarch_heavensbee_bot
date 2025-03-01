ARG BUILDER_TAG
ARG BASE_TAG
ARG DEV_TAG

## Builder
FROM python:${BUILDER_TAG} as builder

WORKDIR /app
COPY src/requirements.txt /app/
RUN python -m venv .venv
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

## Runner
FROM python:${BASE_TAG}${DEV_TAG}

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/plutarch /app/plutarch

ENTRYPOINT [ ".venv/bin/python", "-m", "plutarch" ]