# app/main.py
from fastapi import FastAPI
import os
import server.server as grpc_server

api = FastAPI()
server = grpc_server.PredictionService()

@api.get("/health", response_model=dict)
def health():
    return server.Health()

@api.on_event("startup")
def startup_event():
    server = grpc_server.serve()

@api.get("/predict", response_model=dict, request_model=dict)
def predict(request_data: dict):
    return server.Predict(request_data)
    