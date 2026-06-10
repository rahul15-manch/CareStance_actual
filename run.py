
import uvicorn
import os

if __name__ == "__main__":
<<<<<<< Updated upstream
=======
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
>>>>>>> Stashed changes
    dev_reload = os.getenv("DEV_RELOAD", "false").strip().lower() in ("1", "true", "yes")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=dev_reload,
    )
