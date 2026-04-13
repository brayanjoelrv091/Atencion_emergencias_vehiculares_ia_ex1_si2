from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db, require_cliente
from app.models.user_model import User, Vehicle
from app.schemas.user import MeResponse, UserProfileUpdate
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate

router = APIRouter(prefix="/me", tags=["Perfil y vehículo (cliente)"])


@router.get("", response_model=MeResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    user = (
        db.query(User)
        .options(joinedload(User.vehicles))
        .filter(User.id == current_user.id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.patch("", response_model=MeResponse)
def update_me(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    user = (
        db.query(User)
        .options(joinedload(User.vehicles))
        .filter(User.id == current_user.id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    user = (
        db.query(User)
        .options(joinedload(User.vehicles))
        .filter(User.id == current_user.id)
        .first()
    )
    return user


@router.get("/vehicles", response_model=list[VehicleOut])
def list_my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cliente),
) -> list[Vehicle]:
    return (
        db.query(Vehicle)
        .filter(Vehicle.user_id == current_user.id)
        .order_by(Vehicle.id)
        .all()
    )


@router.post("/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_my_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cliente),
) -> Vehicle:
    v = Vehicle(
        user_id=current_user.id,
        brand=payload.brand,
        model=payload.model,
        license_plate=payload.license_plate.strip().upper(),
        year=payload.year,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut)
def update_my_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cliente),
) -> Vehicle:
    v = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id)
        .first()
    )
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "license_plate" in data and data["license_plate"] is not None:
        data["license_plate"] = data["license_plate"].strip().upper()
    for k, val in data.items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return v


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cliente),
) -> None:
    v = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id)
        .first()
    )
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    db.delete(v)
    db.commit()
