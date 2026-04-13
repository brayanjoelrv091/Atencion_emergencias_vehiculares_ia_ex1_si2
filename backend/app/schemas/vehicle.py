from pydantic import BaseModel, Field


class VehicleCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    license_plate: str = Field(min_length=1, max_length=20)
    year: int | None = Field(default=None, ge=1900, le=2100)


class VehicleUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    license_plate: str | None = Field(default=None, min_length=1, max_length=20)
    year: int | None = Field(default=None, ge=1900, le=2100)


class VehicleOut(BaseModel):
    id: int
    user_id: int
    brand: str
    model: str
    license_plate: str
    year: int | None

    model_config = {"from_attributes": True}
