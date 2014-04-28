#!/bin/bash

rm -rf .git
git init
nlan.py -m
nlan.py init.run
nlan.py -G dvsdvr.yaml
../sit/vglobalip.sh

