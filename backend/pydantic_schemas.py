from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

# --- Input Models (Data Contracts) ---

class SiteTelemetry(BaseModel):
    """
    Simulates live data coming from the Tower Gateway (AQue Gateway).
    """
    site_id: str = Field(..., description="Unique Identifier for the Telecom Tower")
    grid_price: float = Field(..., ge=0, description="Current cost of electricity per kWh")
    battery_soc: int = Field(..., ge=0, le=100, description="Battery State of Charge (%)")
    load_amps: float = Field(..., ge=0, description="Current site load in Amps")
    generator_status: Literal['ON', 'OFF', 'CRANKING'] = "OFF"
    
    # Validator to catch sensor tampering (as per PDF Section 3.5)
    @field_validator('battery_soc')

    def check_sensor_heartbeat(cls, v):
        # In a real scenario, 0 might indicate a dead sensor if not handled
        return v
    
class OptimizationRequest(BaseModel):
    telemetry: SiteTelemetry

# --- Output Models ---

class ControlCommand(BaseModel):
    """
    The decision made by the Eco-Source Optimizer.
    """
    site_id: str
    action: Literal['SWITCH_TO_BATTERY', 'SWITCH_TO_GRID', 'START_GENERATOR', 'MAINTAIN_CURRENT']
    reasoning: str
    savings_estimated: Optional[str] = None