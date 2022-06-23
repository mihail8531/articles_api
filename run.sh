#!/bin/bash
uvicorn articles_api.main:app --reload --ssl-keyfile ./localhost+2-key.pem --ssl-certfile ./localhost+2.pem
