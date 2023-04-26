from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import HTTPException, status
from jose import JWTError
from jose import jwt
from fermerce.lib.errors import error
from fermerce.core.settings import config


class JWTAUTH:
    @staticmethod
    def data_decoder(encoded_data: str, secret_key: str = None):
        try:
            if not secret_key:
                secret_key = config.refresh_secret_key
            else:
                secret_key = secret_key
            payload = jwt.decode(
                token=encoded_data,
                key=secret_key,
                algorithms=[config.algorithm],
            )

            if payload:
                return payload
            raise error.UnauthorizedError("Invalid token provided")

        except JWTError:
            raise error.UnauthorizedError("Invalid token provided")

    @staticmethod
    def data_encoder(
        data: dict,
        duration: Optional[timedelta] = None,
        secret_key: str = None,
        algorithm: str = None,
    ):
        try:
            to_encode = data.copy()
            if duration:
                to_encode.update({"exp": datetime.utcnow() + duration})
            else:
                to_encode.update({"exp": datetime.utcnow() + config.get_refresh_expires_time()})
            encoded_data = jwt.encode(
                claims=to_encode,
                key=secret_key if secret_key else config.refresh_secret_key,
                algorithm=algorithm if algorithm else config.algorithm,
            )
            return encoded_data
        except JWTError:
            raise error.ServerError("Could not complete request please try again")

    @staticmethod
    def jwt_encoder(
        data: dict,
        duration: Union[timedelta, None] = None,
    ):
        access_data = data.copy()
        refresh_data = data.copy()
        if duration:
            access_data.update({"exp": datetime.utcnow() + duration})
            refresh_data.update({"exp": datetime.utcnow() + config.get_refresh_expires_time()})
        else:
            access_data.update({"exp": datetime.utcnow() + config.get_access_expires_time()})
            refresh_data.update({"exp": datetime.utcnow() + config.get_refresh_expires_time()})
        try:
            encode_jwt_refresh = jwt.encode(
                claims=refresh_data,
                key=config.refresh_secret_key,
                algorithm=config.algorithm,
            )
            encode_jwt_access = jwt.encode(
                claims=access_data,
                key=config.secret_key,
                algorithm=config.algorithm,
            )
            return encode_jwt_access, encode_jwt_refresh
        except JWTError:
            raise HTTPException(
                detail={"error": "Error jwt error"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
