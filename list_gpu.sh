#!/bin/bash
# use single quote to avoid expand $HOSTNAME to mgt, but expand $HOSTNAME to gnx
rm -f /data/info/num_cards/gn{1..50}
rm -f /data/info/card_info/gn{1..50}

psh gn[1-50] '/usr/bin/nvidia-smi > /data/info/card_info/${HOSTNAME}' >/dev/null 2>&1 &
pid2=$!
sleep 10
# psh sometimes hangs because of the ssh failures.
kill -SIGINT $pid2

