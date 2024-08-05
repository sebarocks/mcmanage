from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost",
    "http://localhost:5173",
]

corsMiddleware = {
    'middleware_class': CORSMiddleware,
    'allow_origins': origins,
    'allow_credentials': True,
    'allow_methods': ["*"],
    'allow_headers': ["*"],
}
