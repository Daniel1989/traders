from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from celery.result import AsyncResult
from typing import Dict, List
from sqlmodel import Session, select
from pydantic import BaseModel

from app.tasks import add_numbers, fetch_futures_price
from app.celery_app import celery_app
from app.database import init_db, get_session
from app.models import Goods

# Add request model
class GoodsCreate(BaseModel):
    name: str
    title: str | None = None
    description: str | None = None

app = FastAPI(title="FastAPI Celery Example")

@app.on_event("startup")
async def on_startup():
    """Initialize database on startup"""
    result = init_db()
    if result:
        print(f"Database initialization: {result}")

@app.post("/task/add")
async def create_task(x: int, y: int):
    """Create a new Celery task for adding two numbers"""
    task = add_numbers.delay(x, y)
    return {"task_id": task.id}

@app.post("/futures/monitor/{symbol}")
async def monitor_futures(
    symbol: str,
    session: Session = Depends(get_session)
) -> Dict:
    """
    Start monitoring a futures symbol price
    Args:
        symbol: futures symbol (e.g., ag2504)
    Returns:
        Dict containing task_id and monitoring status
    """
    # Basic symbol validation
    if not symbol.isalnum():
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    # Check if goods exists using SQLModel select
    goods_prefix = symbol[:2]
    statement = select(Goods).where(Goods.name == goods_prefix)
    goods = session.exec(statement).first()
    if not goods:
        raise HTTPException(
            status_code=404,
            detail=f"No goods found for symbol prefix: {goods_prefix}"
        )
    
    task = fetch_futures_price.delay(symbol)
    return {
        "task_id": task.id,
        "symbol": symbol,
        "status": "monitoring_started",
        "message": "Price monitoring task has been started"
    }

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """Get the result of a task by its ID"""
    task = AsyncResult(task_id, app=celery_app)
    
    if not task.ready():
        return {
            "status": "PENDING",
            "result": None
        }
    
    result = task.get()
    return {
        "status": "COMPLETED",
        "result": result
    }

@app.post("/goods")
async def create_goods(
    goods_data: GoodsCreate,
    session: Session = Depends(get_session)
) -> Dict:
    """Create a new goods entry"""
    try:
        goods = Goods(
            name=goods_data.name,
            title=goods_data.title,
            description=goods_data.description
        )
        session.add(goods)
        session.commit()
        session.refresh(goods)
        
        return {
            "id": goods.id,
            "name": goods.name,
            "title": goods.title,
            "description": goods.description,
            "created_at": goods.created_at.isoformat(),
            "updated_at": goods.updated_at.isoformat()
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create goods: {str(e)}"
        )

@app.get("/goods")
async def list_goods(
    session: Session = Depends(get_session)
) -> List[Dict]:
    """List all goods"""
    statement = select(Goods)
    goods = session.exec(statement).all()
    return [{
        "id": g.id,
        "name": g.name,
        "title": g.title,
        "description": g.description
    } for g in goods] 