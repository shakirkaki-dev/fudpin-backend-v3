from fastapi import FastAPI

# Routers
from app.routers import restaurant
from app.routers import menu_item
from app.routers import search


app = FastAPI()

# Include Routers
app.include_router(restaurant.router)
app.include_router(menu_item.router)
app.include_router(search.router)


# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {"status": "Fudpin Backend Running"}