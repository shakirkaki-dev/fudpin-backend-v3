from fastapi import FastAPI

# Routers
from app.routers import restaurant
from app.routers import menu_item
from app.routers import search
from app.routers import auth




app = FastAPI()

# Include Routers
app.include_router(restaurant.router)
app.include_router(menu_item.router)
app.include_router(search.router)
app.include_router(auth.router)


# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {"status": "Fudpin Backend Running"}