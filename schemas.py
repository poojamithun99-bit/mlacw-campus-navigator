"""
Pydantic Data Schemas and Validation Models
Ensures strong typing, range verification, and schema validation across campus datasets and API payloads.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class CampusLocationSchema(BaseModel):
    location_id: str = Field(..., description="Unique alphanumeric identifier (e.g. LOC_01)")
    location_name: str = Field(..., description="Canonical English name of the location")
    kannada_name: Optional[str] = Field(None, description="Kannada translation/alias")
    hindi_name: Optional[str] = Field(None, description="Hindi translation/alias")
    category: str = Field(..., description="Classification category (Academic, Lab, Library, etc.)")
    block: str = Field(..., description="Campus block or quadrangle name")
    floor: int = Field(..., ge=0, le=4, description="Floor level (0=Ground, 1, 2, 3)")
    latitude: float = Field(..., ge=13.0110, le=13.0125, description="Geographic latitude within MLACW bounds")
    longitude: float = Field(..., ge=77.5680, le=77.5695, description="Geographic longitude within MLACW bounds")
    is_accessible: bool = Field(True, description="Wheelchair accessible flag")
    has_elevator_access: bool = Field(False, description="Elevator proximity flag")
    description: Optional[str] = Field(None, description="Descriptive campus guide summary")

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_mlacw_bounds(cls, v: float, info):
        # Anchor MLACW Margosa Road bounds
        if info.field_name == "latitude" and not (13.01120 <= v <= 13.01190):
            raise ValueError(f"Latitude {v} falls outside MLACW campus bounds (13.01120 to 13.01190 N).")
        if info.field_name == "longitude" and not (77.56840 <= v <= 77.56920):
            raise ValueError(f"Longitude {v} falls outside MLACW campus bounds (77.56840 to 77.56920 E).")
        return v

class DepartmentSchema(BaseModel):
    department_id: str
    department_name: str
    kannada_name: Optional[str] = None
    hindi_name: Optional[str] = None
    block: str
    floor: int
    location_id: Optional[str] = None
    hod_name: Optional[str] = None
    contact_email: Optional[str] = None
    phone_ext: Optional[str] = None

class ClassroomSchema(BaseModel):
    classroom_id: str
    room_number: str
    room_name: str
    block: str
    floor: int
    capacity: int = Field(..., ge=1, le=500)
    facilities: Optional[str] = None
    is_wheelchair_accessible: bool = True
    department_id: Optional[str] = None
    location_id: Optional[str] = None

class NavigationPathSchema(BaseModel):
    path_id: str
    source_node: str
    target_node: str
    distance_meters: float = Field(..., gt=0)
    path_type: Literal["Corridor", "Stairs", "Elevator", "Ramp", "Open Walkway"]
    is_accessible: bool = True
    crowd_level: Literal["Low", "Medium", "High"] = "Low"
    transition_type: Literal["Horizontal", "Vertical"] = "Horizontal"

class RoutingRequestSchema(BaseModel):
    start_node: str
    dest_node: str
    language: Literal["English", "Kannada", "Hindi"] = "English"
    wheelchair_mode: bool = False
    crowd_multiplier: float = Field(1.0, ge=1.0, le=2.5)

class StepGuidanceSchema(BaseModel):
    step: int
    action_type: str
    instruction: str
    audio_text: str
    distance: int
    icon: str
    current_floor: str
    target_floor: str
    from_node: str
    to_node: str
    path_type: str

class RoutingResponseSchema(BaseModel):
    start_node: str
    dest_node: str
    path: List[str]
    total_distance_meters: float
    estimated_time_minutes: float
    is_wheelchair_accessible: bool
    steps: List[StepGuidanceSchema]
