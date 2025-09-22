from fastapi import FastAPI
from routes.route import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router)

origins = [
    "http://localhost:3000",  # React dev server
    # "https://your-frontend-domain.vercel.app"  # deployed frontend (if applicable)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if __name__ == "__main__": 
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)