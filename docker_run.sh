#!/bin/bash
sudo docker run -p 5000:80 -it --rm --name bigsense-en -v $(pwd)/best_model:/model textimager-bigsense-en
