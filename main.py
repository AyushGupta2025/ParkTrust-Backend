from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
import time
import random

# Initialize the App
app = FastAPI(title="ParkTrust: Immutable Parking Enforcement")

# --- DATA MODELS ---
class CarEntry(BaseModel):
    plate_number: str = "DL-10-AB-1234"
    entry_gate_id: str = "Gate_A"

# --- MOCK DATA (Simulating the Parking Lot) ---
PARKING_SLOTS = [
    {"id": "A1", "x": 0, "y": 10, "occupied": False},
    {"id": "A2", "x": 0, "y": 20, "occupied": False},
    {"id": "B1", "x": 20, "y": 10, "occupied": True}, # Full
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

    # 1. Find Available Slots
    available = [s for s in PARKING_SLOTS if not s["occupied"]]
    if not available:
        return {"status": "DENIED", "reason": "Parking Full"}

    # 2. Run Least Distance Algorithm
    best_slot = min(available, key=lambda s: calculate_manhattan_distance(
        gate_pos["x"], gate_pos["y"], s["x"], s["y"]
    ))

    # 3. Simulate Blockchain Logging
    tx_hash = f"hash_{random.randint(100000,999999)}_{int(time.time())}"
    
    return {
        "ticket_id": f"TKT-{int(time.time())}",
        "assigned_slot": best_slot["id"],
        "directions": f"Go to Grid ({best_slot['x']}, {best_slot['y']})",
        "blockchain_hash": tx_hash,
        "message": "Entry logged to Immutable Ledger"
    }

@app.get("/mcd-dashboard")
def view_audit_logs():
    return {
        "alert_level": "NORMAL",
        "recent_logs": [
            {"time": "10:01 AM", "event": "ENTRY", "plate": "DL-10-CA-1234", "hash": "verified_safe"},
            {"time": "10:05 AM", "event": "TAMPER_ATTEMPT", "plate": "UNKNOWN", "hash": "ALERT_TRIGGERED"}
        ]
    }