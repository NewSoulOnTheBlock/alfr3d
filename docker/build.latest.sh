#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/Dockerfile.latest \
             -t newsoulontheblock/alfr3d .

docker tag newsoulontheblock/alfr3d newsoulontheblock/alfr3d:$(date +%y%m%d)