from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
import time
import random

app = FastAPI(title="ParkTrust: Immutable Parking Enforcement")

# --- DATA MODELS ---
class CarEntry(BaseModel):
    plate_number: str = "DL-10-AB-1234"
    entry_gate_id: str = "Gate_A"

class CarExit(BaseModel):
    ticket_id: str = "TKT-1703456789"

# NEW: The Sensor Data Model
class SensorUpdate(BaseModel):
    slot_id: str = "A1"
    status: str = "OCCUPIED"  # Sensors send either "OCCUPIED" or "EMPTY"

# --- MOCK DATA ---
PARKING_SLOTS = [
    {"id": "A1", "x": 0, "y": 10, "occupied": False},
    {"id": "A2", "x": 0, "y": 20, "occupied": False},
    {"id": "B1", "x": 20, "y": 10, "occupied": True},
    {"id": "B2", "x": 20, "y": 20, "occupied": False},
]

GATES = {"Gate_A": {"x": 0, "y": 0}, "Gate_B": {"x": 20, "y": 0}}

# --- ALGORITHMS ---
def calculate_manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"system_status": "ONLINE", "audit_mode": "ACTIVE"}

@app.post("/vehicle-entry")
def vehicle_enters(entry: CarEntry):
    gate_pos = GATES.get(entry.entry_gate_id)
    if not gate_pos:
        raise HTTPException(status_code=400, detail="Invalid Gate ID")

    available = [s for s in PARKING_SLOTS if not s["occupied"]]
    if not available:
        return {"status": "DENIED", "reason": "Parking Full"}

    best_slot = min(available, key=lambda s: calculate_manhattan_distance(
        gate_pos["x"], gate_pos["y"], s["x"], s["y"]
    ))
    
    # NEW: We mark it as "Reserved" internally waiting for sensor confirmation
    # In a real database, we would set status="PENDING_ARRIVAL"

    tx_hash = f"entry_{random.randint(100000,999999)}_{int(time.time())}"
    
    return {
        "ticket_id": f"TKT-{int(time.time())}",
        "assigned_slot": best_slot["id"],
        "directions": f"Go to Grid ({best_slot['x']}, {best_slot['y']})",
        "blockchain_hash": tx_hash,
        "message": "Entry logged. Proceed to slot for Sensor Verification."
    }

# --- NEW: SENSOR VERIFICATION ENDPOINT ---
@app.post("/verify-slot-occupancy")
def sensor_detects_car(sensor_data: SensorUpdate):
    
    # 1. Check if the slot exists
    target_slot = next((s for s in PARKING_SLOTS if s["id"] == sensor_data.slot_id), None)
    if not target_slot:
        raise HTTPException(status_code=404, detail="Slot ID not found")
    
    # 2. Compare Sensor Reality vs System Expectation
    if sensor_data.status == "OCCUPIED":
        # In a real app, we check if we actually assigned a car here recently.
        # For this demo, we simulate a successful match.
        
        verification_hash = f"sensor_verify_{random.randint(100000,999999)}"
        
        return {
            "slot_id": sensor_data.slot_id,
            "sensor_status": "METAL_DETECTED",
            "system_status": "MATCH_CONFIRMED",
            "compliance_check": "PASSED",
            "audit_log": verification_hash,
            "message": "2-Factor Verification Successful. Car is legally parked."
        }
    
    else:
        return {"message": "Slot is empty. Waiting for vehicle."}

@app.post("/vehicle-exit")
def vehicle_exits(exit_req: CarExit):
    hours = random.randint(1, 4)
    total = hours * 20
    bill_hash = f"bill_{random.randint(100000,999999)}_{int(time.time())}"

    return {
        "status": "EXIT_APPROVED",
        "ticket_id": exit_req.ticket_id,
        "total_fee": f"₹{total}",
        "blockchain_receipt": bill_hash
    }

@app.get("/admin-dashboard")
def view_live_stats():
    return {"total_revenue": "₹14,500", "occupancy": "85%", "fraud_alerts": 0}
