#!/bin/bash

source .venv/bin/activate

clear

echo "Starting Ansiversa API..."

uvicorn app.main:app --reload