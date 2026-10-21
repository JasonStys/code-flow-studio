# Polyglot compiler worker; trusted build inputs only. Never contains provider keys.
# Fixed compile/run adapters are documented in docs/languages.md.
FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS dotnet
FROM node:24-bookworm-slim AS node
FROM python:3.12.12-slim-bookworm
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
ENV DOTNET_ROOT=/usr/share/dotnet PATH="/usr/share/dotnet:${PATH}" DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends clang llvm-14 libclang-rt-14-dev gcc g++ openjdk-17-jdk-headless php-cli php-xdebug php-xml php-mbstring rustc cargo nasm sqlite3 bash shellcheck shfmt valgrind afl++ libicu72 curl unzip ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.4.2 coverage==7.11.0 hypothesis==6.142.4 atheris==3.0.0 sqlfluff==4.4.0 && npm install --global typescript@5.9.3
COPY tools/package*.json /opt/tools/
RUN npm ci --prefix /opt/tools --ignore-scripts && npm audit --prefix /opt/tools --omit=dev --audit-level=high
RUN curl -fL --retry 3 https://github.com/jacoco/jacoco/releases/download/v0.8.15/jacoco-0.8.15.zip -o /tmp/jacoco.zip && echo '5b3f6ddb724e761d25c937d68b0189a3a23f3e220e3282575ee0b53359e8110e  /tmp/jacoco.zip' | sha256sum -c - && unzip -q /tmp/jacoco.zip -d /opt/jacoco && rm /tmp/jacoco.zip
RUN curl -fL --retry 3 https://github.com/pmd/pmd/releases/download/pmd_releases/7.28.0/pmd-dist-7.28.0-bin.zip -o /tmp/pmd.zip && echo 'f974ba571f7bc01c73fffe11bade25fbc1f438698f9e9c00e416e8d65e9fbac2  /tmp/pmd.zip' | sha256sum -c - && unzip -q /tmp/pmd.zip -d /opt && rm /tmp/pmd.zip
RUN curl -fL --retry 3 https://github.com/phpmd/phpmd/releases/download/3.0.0/phpmd.phar -o /opt/phpmd.phar && echo '0d6ba223b7bf41119e02e1ef23faac3cb93e5f0fc6d06ea42211873edf6a8236  /opt/phpmd.phar' | sha256sum -c -
RUN dotnet tool install coverlet.console --version 8.0.1 --tool-path /opt/coverlet
COPY *.py *.cjs *.php *.sh *.xml /opt/
RUN mkdir /input && chmod 755 /input
USER 65534:65534
WORKDIR /tmp
ENTRYPOINT ["python", "/opt/worker.py"]

