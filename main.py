import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared import security
from shared.dependencies import get_db
from stock.routes import auth, categories, products, shopping_cart, purchase, dashboard
from stock.models.user import User
from shared.security import get_password_hash

load_dotenv()
DEFAULT_EMAIL=os.getenv('DEFAULT_EMAIL')
DEFAULT_PASSWORD=os.getenv('DEFAULT_PASSWORD')
DEFAULT_USERNAME= os.getenv('DEFAULT_USERNAME')
CORE_PORT=int(os.getenv('CORE_PORT'))

def create_default_user(db: Session):
    default_username = DEFAULT_USERNAME
    default_email = DEFAULT_EMAIL
    default_password = DEFAULT_PASSWORD

    user = db.query(User).filter(User.username == default_username).first()
    if user:
        user.email = default_email
        user.hashed_password = get_password_hash(default_password)
        db.commit()
        print(f"Default user updated: {default_username}")
    else:
        hashed_password = get_password_hash(default_password)
        new_user = User(username=default_username, email=default_email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Default user created: {default_username}")


async def startup():
    db: Session = next(get_db())
    create_default_user(db)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)




@app.on_event("startup")
async def startup_event():
    await startup()

# routers
app.include_router(auth.router)
app.include_router(categories.router, dependencies=[Depends(security.get_current_user)])
app.include_router(products.router, dependencies=[Depends(security.get_current_user)])
app.include_router(shopping_cart.router, dependencies=[Depends(security.get_current_user)])
app.include_router(purchase.router, dependencies=[Depends(security.get_current_user)])
app.include_router(dashboard.router,  dependencies=[Depends(security.get_current_user)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=CORE_PORT)
