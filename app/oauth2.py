from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
#SECRET_KEY
#ALGO HS256
#EXPIRATION TIME

SECRET_KEY = settings.secret_key
ALGO = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_mins

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)

    return jwt_token

def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGO])
        id: str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id = id)

    except JWTError:
        raise credentials_exception

    return token_data

    
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail=f"could not validate credentials", headers={
        "WWW-Authenticate": "Bearer"
    })
    
    token_verify = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token_verify.id).first()

    return user
