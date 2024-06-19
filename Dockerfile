FROM python:3-alpine AS node-build
WORKDIR /build

RUN apk add --no-cache \
	cmake \
	build-base \
	git

COPY requirements.txt .
RUN pip3 wheel -r requirements.txt


FROM python:3-alpine
WORKDIR /app

COPY --from=node-build /build/*.whl /app/pkgs/

RUN apk add --no-cache \
	libstdc++

RUN pip3 install /app/pkgs/*.whl
COPY src .

CMD [ "/usr/local/bin/python", "-u", "/app/main.py" ]
