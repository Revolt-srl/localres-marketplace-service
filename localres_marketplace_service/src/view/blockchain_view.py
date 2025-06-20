from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBearer

from localres_marketplace_service.src.blockchain.user import UserViewModel, UserWriteModel
from localres_marketplace_service.src.blockchain.blockchain_manager import BlockchainManager
from localres_marketplace_service.src.common.auth import admin_authorize, user_authorize

blockchain_router = APIRouter()


@blockchain_router.get("/blockchain/user/{user_id}", tags=["blockchain"])
@user_authorize
def get_user_value(request: Request, user_id: str, token=Depends(HTTPBearer())):
    blockchain_manager: BlockchainManager = request.app.state.blockchain_manager
    resp = blockchain_manager.get_user_value(user_id)
    if resp.is_err:
        return Response(content=str(resp.unwrap_err()), status_code=500)
    return resp.unwrap()


@blockchain_router.get("/blockchain/user", tags=["blockchain"])
@user_authorize
def get_all_users(request: Request, token=Depends(HTTPBearer())):
    blockchain_manager: BlockchainManager = request.app.state.blockchain_manager
    resp = blockchain_manager.get_user_value("all")
    if resp.is_err:
        return Response(content=str(resp.unwrap_err()), status_code=500)
    return resp.unwrap()


@blockchain_router.put("/blockchain/user", tags=["blockchain"])
@admin_authorize
def upsert_user(request: Request, user: UserViewModel, token=Depends(HTTPBearer())):
    wm: UserWriteModel = user.to_write_model()
    blockchain_manager: BlockchainManager = request.app.state.blockchain_manager
    resp = blockchain_manager.upsert_user(wm)
    if resp.is_err:
        return Response(content=str(resp.unwrap_err()), status_code=500)
    return resp.unwrap()


@blockchain_router.delete("/blockchain/user/{user_id}", tags=["blockchain"])
@admin_authorize
def delete_user(request: Request, user_id: str, token=Depends(HTTPBearer())):
    blockchain_manager: BlockchainManager = request.app.state.blockchain_manager
    resp = blockchain_manager.delete_user(user_id)
    if resp.is_err:
        return Response(content=str(resp.unwrap_err()), status_code=500)
    return resp.unwrap()
