#!/bin/bash
while ! /bin/ss -H -t -l -n sport = :2333 | /bin/grep -q "^LISTEN.*:2333";
do /bin/sleep 1;
done;
export PATH=$HOME/.local/.bin:$PATH;  # Add local bin to PATH - required for pipx-installed poetry
poetry run python -m bot;
