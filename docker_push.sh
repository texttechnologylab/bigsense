#!/bin/bash
IMAGE_VER=2
bash ./docker_build.sh
sudo docker tag textimager-bigsense-en texttechnologylab/textimager-bigsense-en:${IMAGE_VER}
sudo docker push texttechnologylab/textimager-bigsense-en:${IMAGE_VER}
