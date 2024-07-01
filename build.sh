#!/usr/bin/env bash
pandoc \
	-V colorlinks=true \
	-V papersize=a4 \
	--from=gfm --to=pdf README.md -o README.pdf
exit 0
