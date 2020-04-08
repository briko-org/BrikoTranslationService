#!/bin/sh

python3 translator_service.py &
python3 api_service.py
