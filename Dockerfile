FROM ubuntu:22.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install ca-certificates \
        gcc wget python3 python3-pip -y

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.67.1

RUN set -eux; \
    rustArch='x86_64-unknown-linux-musl'; rustupSha256='241a99ff02accd2e8e0ef3a46aaa59f8d6934b1bb6e4fba158e1806ae028eb25' ; \
    url="https://static.rust-lang.org/rustup/archive/1.25.2/${rustArch}/rustup-init"; \
    wget "$url"; \
    echo "${rustupSha256} *rustup-init" | sha256sum -c -; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --profile minimal --default-toolchain $RUST_VERSION --default-host ${rustArch}; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; 
LABEL maintainer="waso"

COPY ./libfptr10_10.9.4.5_amd64.deb ./
COPY ./libfptr10.py ./
COPY ./main.py ./
COPY ./api_server.py ./
COPY ./requirements.txt ./
COPY ./.env ./

EXPOSE 8888

RUN python3 -V
RUN pip3 install --upgrade pip
RUN pip3 install wheel setuptools pip --upgrade 
RUN pip3 install -r requirements.txt 
RUN dpkg -i libfptr10_10.9.4.5_amd64.deb

CMD python3 api_server.py
