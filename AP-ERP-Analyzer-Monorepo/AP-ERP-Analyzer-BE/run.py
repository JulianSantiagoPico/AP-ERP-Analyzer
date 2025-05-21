#!/usr/bin/env python3
# Copyright 2025 Anti-Patrones
# This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.
# http://creativecommons.org/licenses/by-sa/4.0/

import os
import uvicorn
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5002
    debug = True
    
    print(f"Iniciando servidor en {host}:{port} (Debug: {debug})")
    uvicorn.run("run:app", host=host, port=port, reload=debug)