#!/bin/bash

clear
echo ""

curl -X POST \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"text": "What a great MLOps lecture, I am very satisfied"}'

echo ""
echo ""