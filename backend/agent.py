from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from backend.pydantic_schemas import SiteTelemetry, ControlCommand

# 1. Define the Agent State
# We make 'decision' Optional so the graph can start with just 'telemetry'
class AgentState(TypedDict):
    telemetry: SiteTelemetry
    decision: Optional[ControlCommand] 

# 2. Define Constants
PEAK_PRICE_THRESHOLD = 0.20
BATTERY_SAFE_LIMIT = 30
BATTERY_FULL_ENOUGH = 80

# 3. Define Nodes
def analyze_economics(state: AgentState):
    """
    Analyses costs. Logic: 'Cheapest Electron' decision tree.
    """
    data = state['telemetry']
    
    # Logic 1: Peak Shaving
    if data.grid_price >= PEAK_PRICE_THRESHOLD and data.battery_soc > BATTERY_SAFE_LIMIT:
        return {
            "decision": ControlCommand(
                site_id=data.site_id,
                action="SWITCH_TO_BATTERY",
                reasoning=f"Price ({data.grid_price}) is High. Battery has capacity ({data.battery_soc}%).",
                savings_estimated="High"
            )
        }
        
    # Logic 2: Low Battery Protection
    if data.battery_soc < BATTERY_SAFE_LIMIT:
        return {
            "decision": ControlCommand(
                site_id=data.site_id,
                action="SWITCH_TO_GRID",
                reasoning=f"Battery low ({data.battery_soc}%). Must charge from Grid.",
                savings_estimated="None (Safety Priority)"
            )
        }

    # Default: Use Grid
    return {
        "decision": ControlCommand(
            site_id=data.site_id,
            action="MAINTAIN_CURRENT",
            reasoning="Grid price is normal and battery is stable.",
            savings_estimated="Standard"
        )
    }

# 4. Build the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("optimizer_logic", analyze_economics)

# Set entry point
workflow.set_entry_point("optimizer_logic")

# Set finish point
workflow.add_edge("optimizer_logic", END)

# Compile
eco_source_agent = workflow.compile()