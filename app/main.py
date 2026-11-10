from fastapi import FastAPI

app = FastAPI(title="Linux Automated Deployment")


@app.get("/")
def root():
    return {"message": "FastAPI is running in Docker"}


@app.get("/health")
def health():
    return {"status": "ok"}