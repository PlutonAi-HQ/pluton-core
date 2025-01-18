#! /bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m uvicorn app.main:app --reload --port 3456