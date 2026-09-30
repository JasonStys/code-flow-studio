# Polyglot compiler worker; trusted build inputs only. Never contains provider keys.
# Fixed compile/run adapters are documented in docs/languages.md.
FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS dotnet
FROM python:3.12.12-slim-bookworm
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
ENV DOTNET_ROOT=/usr/share/dotnet PATH="/usr/share/dotnet:${PATH}" DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends clang libclang-rt-14-dev gcc g++ openjdk-17-jdk-headless php-cli nodejs npm rustc cargo nasm sqlite3 bash afl++ libicu72 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.4.2 coverage==7.11.0 hypothesis==6.142.4 atheris==3.0.0 && npm install --global typescript@5.9.3
COPY worker.py /opt/worker.py
RUN mkdir /input && chmod 755 /input
USER 65534:65534
WORKDIR /tmp
ENTRYPOINT ["python", "/opt/worker.py"]

