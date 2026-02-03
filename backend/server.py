from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from backend.pydantic_schemas import OptimizationRequest, ControlCommand, SiteTelemetry
from backend.agent import eco_source_agent

app = FastAPI(title="AxIn Energy AI Platform", version="1.0.0")

@app.get("/")
def read_root():
    return {"status": "AxIn Energy Brain is Running"}

@app.post("/optimize", response_model=ControlCommand)
async def run_optimizer(request: OptimizationRequest):
    """
    Endpoint exposed to Flowise.
    Receives Telemetry -> Runs LangGraph Agent -> Returns Control Decision.
    """
    try:
        # 1. Initialize State
        # FIX: Explicitly initialize 'decision' to None to satisfy TypedDict 
        # (even if Optional, explicit initialization prevents runtime ambiguities)
        initial_state = {
            "telemetry": request.telemetry,
            "decision": None
        }
        
        # 2. Run the Agent
        # The agent returns the FINAL state (a dict)
        result_state = eco_source_agent.invoke(initial_state)
        
        # 3. Extract Decision
        decision = result_state.get("decision")
        
        if not decision:
            raise HTTPException(status_code=500, detail="Agent logic completed but returned no decision.")
            
        return decision

    except Exception as e:
        # Log the actual error for easier debugging
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Reload=True helps during development
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)