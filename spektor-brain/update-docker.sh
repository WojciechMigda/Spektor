#!/bin/sh

for fn in main.py spektor_impl.py spektor_core.py; do
    docker cp src/service/$fn spektor:/webapp/service/$fn
done
