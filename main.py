import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Trainer, GymClass, MembershipPlan, Lead, Booking

app = FastAPI(title="Gym Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Gym Pro Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "❌ Not Available"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# --------- Bootstrap sample data (idempotent) ---------
@app.post("/api/bootstrap")
def bootstrap_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    inserted = {"trainer": 0, "gymclass": 0, "membershipplan": 0}

    # Trainers
    if db["trainer"].count_documents({}) == 0:
        trainers = [
            Trainer(name="Ava Stone", specialty="Strength & Conditioning", bio="Former national powerlifter coaching efficient, injury-safe strength.", experience_years=8, avatar_url=None),
            Trainer(name="Leo Cruz", specialty="HIIT & Fat Loss", bio="Explosive, science-backed fat-loss programming.", experience_years=6, avatar_url=None),
            Trainer(name="Maya Chen", specialty="Mobility & Yoga", bio="Restore movement, build core control, breathe better.", experience_years=9, avatar_url=None),
        ]
        for t in trainers:
            create_document("trainer", t)
            inserted["trainer"] += 1

    # Classes
    if db["gymclass"].count_documents({}) == 0:
        # Fetch any trainer ids to attach optionally
        trainer_ids = [str(d.get("_id")) for d in db["trainer"].find({}).limit(3)]
        classes = [
            GymClass(title="Power HIIT", description="High-intensity intervals with compound moves.", difficulty="Intermediate", duration_minutes=45, trainer_id=trainer_ids[1] if len(trainer_ids) > 1 else None, schedule=["Mon 07:00", "Wed 18:00", "Fri 07:00"]),
            GymClass(title="Barbell Fundamentals", description="Technique-first strength training.", difficulty="Beginner", duration_minutes=60, trainer_id=trainer_ids[0] if len(trainer_ids) > 0 else None, schedule=["Tue 17:00", "Thu 17:00"]),
            GymClass(title="Mobility Flow", description="Joint prep, core, and breath-led flow.", difficulty="All Levels", duration_minutes=50, trainer_id=trainer_ids[2] if len(trainer_ids) > 2 else None, schedule=["Sat 09:30"]),
        ]
        for c in classes:
            create_document("gymclass", c)
            inserted["gymclass"] += 1

    # Plans
    if db["membershipplan"].count_documents({}) == 0:
        plans = [
            MembershipPlan(name="Starter", price_monthly=29, features=["Gym Access", "Locker", "Open Gym"]),
            MembershipPlan(name="Pro", price_monthly=59, features=["All Starter", "Unlimited Classes", "Program Audit"], best_value=True),
            MembershipPlan(name="Elite", price_monthly=99, features=["All Pro", "1:1 Coaching", "Priority Booking", "Recovery Suite"]),
        ]
        for p in plans:
            create_document("membershipplan", p)
            inserted["membershipplan"] += 1

    return {"status": "ok", "inserted": inserted}


# --------- Public API ---------

@app.get("/api/trainers")
def list_trainers():
    try:
        docs = get_documents("trainer")
        # Convert ObjectId to string
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/classes")
def list_classes():
    try:
        docs = get_documents("gymclass")
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans")
def list_plans():
    try:
        docs = get_documents("membershipplan")
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads")
def create_lead(payload: Lead):
    try:
        _id = create_document("lead", payload)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bookings")
def create_booking(payload: Booking):
    try:
        _id = create_document("booking", payload)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
