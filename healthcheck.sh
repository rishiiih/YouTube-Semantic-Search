#!/bin/bash

# Health check endpoint
curl -f http://localhost:$PORT/health || exit 1
