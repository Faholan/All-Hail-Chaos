#!/bin/sh
while ! /bin/ss -H -t -l -n sport = :2333 | /bin/grep -q "^LISTEN.*:2333";
do /bin/sleep 1;
done;
source venv/bin/activate;
python3 -m bot;
