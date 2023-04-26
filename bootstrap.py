from fermerce.core.settings import config
import uvicorn


def run_server():
    uvicorn.run("main:app", reload=config.debug, workers=8)


if __name__ == "__main__":
    run_server()
