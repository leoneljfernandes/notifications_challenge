from sqlalchemy import text
def check_all_services():
    return {"status": "ok"}

def check_system(db):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "details": str(e)}
