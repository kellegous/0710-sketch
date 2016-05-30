#!/bin/bash

HERE=$(cd $(dirname $BASH_SOURCE); pwd)

if [ ! -d "$HERE/.env/sketching" ]; then
	virtualenv --system-site-packages "$HERE/.env/sketching"
fi

source "$HERE/.env/sketching/bin/activate"

pip install -r "${HERE}/requirements.txt"