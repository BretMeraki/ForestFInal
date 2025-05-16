# forest_app/routers/auth.py

import logging
from datetime import timedelta
<<<<<<< HEAD
from typing import Optional # Added Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
# --- Pydantic Imports ---
from pydantic import BaseModel, Field, EmailStr # Import base pydantic needs

# --- Dependencies & Models ---
from forest_app.persistence.database import get_db
from forest_app.persistence.repository import get_user_by_email, create_user
from forest_app.persistence.models import UserModel
from forest_app.core.security import (
    verify_password, create_access_token, get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
=======
from typing import Optional  # Added Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# --- Pydantic Imports ---
from pydantic import BaseModel, EmailStr, Field  # Import base pydantic needs
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from forest_app.core.security import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                      create_access_token, get_password_hash,
                                      verify_password)
# --- Dependencies & Models ---
from forest_app.persistence.database import get_db
from forest_app.persistence.repository import create_user, get_user_by_email

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- REMOVED INCORRECT IMPORT ---
# from forest_app.core.pydantic_models import Token, UserCreate, UserRead # Assuming models are moved/centralized
try:
    from forest_app.config import constants
except ImportError:
<<<<<<< HEAD
    class ConstantsPlaceholder: MIN_PASSWORD_LENGTH = 8; ONBOARDING_STATUS_NEEDS_GOAL="needs_goal"
=======

    class ConstantsPlaceholder:
        MIN_PASSWORD_LENGTH = 8
        ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    constants = ConstantsPlaceholder()


logger = logging.getLogger(__name__)
router = APIRouter()

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- Pydantic Models DEFINED LOCALLY ---
# Define models needed specifically by this router
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

<<<<<<< HEAD
class UserBase(BaseModel): # Base needed for others
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=constants.MIN_PASSWORD_LENGTH)

=======

class UserBase(BaseModel):  # Base needed for others
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=constants.MIN_PASSWORD_LENGTH)


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class UserRead(UserBase):
    id: int
    is_active: bool
    onboarding_status: Optional[str] = None
<<<<<<< HEAD
    class Config: from_attributes = True
=======

    class Config:
        from_attributes = True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- End Pydantic Models ---


@router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(
<<<<<<< HEAD
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
=======
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
):
    # Function body remains the same...
    logger.debug("Login attempt for email: %s", form_data.username)
    try:
        user = get_user_by_email(db, email=form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
<<<<<<< HEAD
            logger.warning("Login failed for email %s: Incorrect email or password.", form_data.username)
=======
            logger.warning(
                "Login failed for email %s: Incorrect email or password.",
                form_data.username,
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
<<<<<<< HEAD
        if hasattr(user, 'is_active') and not user.is_active:
             logger.warning("Login failed for email %s: User is inactive.", user.email)
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
=======
        if hasattr(user, "is_active") and not user.is_active:
            logger.warning("Login failed for email %s: User is inactive.", user.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        logger.info("User %s logged in successfully.", user.email)
        return Token(access_token=access_token, token_type="bearer")

<<<<<<< HEAD
    except HTTPException: raise
    except SQLAlchemyError as db_err:
        logger.exception("Database error during login for %s: %s", form_data.username, db_err)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error during login. Please try again later."
        )
    except Exception as e:
        logger.exception("Unexpected error during login for %s: %s", form_data.username, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login."
        )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
=======
    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.exception(
            "Database error during login for %s: %s", form_data.username, db_err
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error during login. Please try again later.",
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during login for %s: %s", form_data.username, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login.",
        )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Function body remains the same...
    logger.info("Registration attempt for email: %s", user_in.email)
    try:
        db_user = get_user_by_email(db, email=user_in.email)
        if db_user:
<<<<<<< HEAD
            logger.warning("Registration failed for %s: Email already registered.", user_in.email)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = get_password_hash(user_in.password)
        user_data = {
            "email": user_in.email, "hashed_password": hashed_password,
            "full_name": user_in.full_name, "is_active": True
=======
            logger.warning(
                "Registration failed for %s: Email already registered.", user_in.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user_in.password)
        user_data = {
            "email": user_in.email,
            "hashed_password": hashed_password,
            "full_name": user_in.full_name,
            "is_active": True,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }
        created_user = create_user(db=db, user_data=user_data)

        if not created_user:
<<<<<<< HEAD
            logger.error("create_user function returned None for email %s. Checking for race condition.", user_in.email)
            if get_user_by_email(db, email=user_in.email):
                 logger.warning("Registration failed for %s due to likely concurrent request.", user_in.email)
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered (concurrent request likely)")
            else:
                 logger.error("Failed to create user model for %s for unknown reason.", user_in.email)
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user model.")

        logger.info("User %s registered successfully (ID: %s). Preparing response.", created_user.email, getattr(created_user, 'id', 'Pending'))
        response_data = UserRead.model_validate(created_user, from_attributes=True).model_dump()
        response_data["onboarding_status"] = constants.ONBOARDING_STATUS_NEEDS_GOAL
        return UserRead.model_validate(response_data)

    except HTTPException: raise
    except SQLAlchemyError as db_err:
        logger.exception("Database error during registration for %s: %s", user_in.email, db_err)
        if "UNIQUE constraint failed" in str(db_err) or "duplicate key value violates unique constraint" in str(db_err).lower():
             logger.warning("Registration failed for %s due to unique constraint (likely email).", user_in.email)
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error during registration.")
    except Exception as e:
        logger.exception("Unexpected error during registration for %s: %s", user_in.email, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during registration.")
=======
            logger.error(
                "create_user function returned None for email %s. Checking for race condition.",
                user_in.email,
            )
            if get_user_by_email(db, email=user_in.email):
                logger.warning(
                    "Registration failed for %s due to likely concurrent request.",
                    user_in.email,
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered (concurrent request likely)",
                )
            else:
                logger.error(
                    "Failed to create user model for %s for unknown reason.",
                    user_in.email,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user model.",
                )

        logger.info(
            "User %s registered successfully (ID: %s). Preparing response.",
            created_user.email,
            getattr(created_user, "id", "Pending"),
        )
        response_data = UserRead.model_validate(
            created_user, from_attributes=True
        ).dict()
        response_data["onboarding_status"] = constants.ONBOARDING_STATUS_NEEDS_GOAL
        return UserRead.model_validate(response_data)

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.exception(
            "Database error during registration for %s: %s", user_in.email, db_err
        )
        if (
            "UNIQUE constraint failed" in str(db_err)
            or "duplicate key value violates unique constraint" in str(db_err).lower()
        ):
            logger.warning(
                "Registration failed for %s due to unique constraint (likely email).",
                user_in.email,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error during registration.",
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during registration for %s: %s", user_in.email, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration.",
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
