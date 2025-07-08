#!/bin/bash

uvicorn inference_server_vllm:app --host 0.0.0.0 --port 8083

# curl -X POST http://localhost:8083/chat -H "Content-Type: application/json" -d '{"user_query": "读取文件 /tmp/test.txt"}'


