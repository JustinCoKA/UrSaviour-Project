from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, MetaData, Table
from app.db.session import get_db, engine
from app.db.models.user import User
from app.schemas.user import UserOut, UserCreate
from app.services.auth import hash_password
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Schema for user updates
class UserUpdate(BaseModel):
    firstName: str = None
    lastName: str = None
    email: str = None
    password: str = None

# Lazily load ETL Jobs table
metadata = MetaData()
_etl_tables_loaded = False
ETLJobs = None

def _ensure_etl_tables():
    global _etl_tables_loaded, ETLJobs
    if not _etl_tables_loaded:
        ETLJobs = Table("etlJobs", metadata, autoload_with=engine)
        _etl_tables_loaded = True

@router.get("/etl-jobs", summary="Get all ETL jobs")
def get_etl_jobs(db: Session = Depends(get_db)):
    """
    Get all ETL jobs from the database
    Returns: List of ETL job records
    """
    try:
        _ensure_etl_tables()
        
        # Get available columns dynamically
        available_cols = {col.name for col in ETLJobs.columns}
        logger.info(f"Available columns in etlJobs table: {available_cols}")
        
        # Build query with only available columns
        select_cols = []
        col_mapping = {
            'jobId': 'jobId',
            'jobNumber': 'jobNumber',
            'jobType': 'jobType',
            'sourceFile': 'sourceFile',
            'sourceIdentifier': 'sourceIdentifier',
            'startTime': 'startTime',
            'endTime': 'endTime',
            'overallStatus': 'overallStatus',
            'totalItemExtracted': 'totalItemExtracted',
            'totalItemLoaded': 'totalItemLoaded',
            'totalItemFailed': 'totalItemFailed',
            'errorLog': 'errorLog'
        }
        
        for col_name in col_mapping.keys():
            if col_name in available_cols:
                select_cols.append(ETLJobs.c[col_name])
        
        query = select(*select_cols).order_by(ETLJobs.c.startTime.desc()).limit(100)
        result = db.execute(query).fetchall()
        
        # Convert to list of dicts
        jobs = []
        for row in result:
            job = {}
            for col_name, json_name in col_mapping.items():
                if col_name in available_cols:
                    value = getattr(row, col_name, None)
                    # Convert datetime to ISO format
                    if value and col_name in ['startTime', 'endTime']:
                        job[json_name] = value.isoformat()
                    else:
                        job[json_name] = value
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching ETL jobs: {str(e)}")
        return {"error": str(e), "message": "Failed to fetch ETL jobs"}

# ==================== Login Logs Endpoint ====================

@router.get("/login-logs", summary="Get all login logs")
def get_login_logs(db: Session = Depends(get_db)):
    """Get all login logs (admin only)"""
    try:
        from app.db.models.login_log import LoginLog
        
        logs = db.query(LoginLog).order_by(LoginLog.attempted_at.desc()).all()
        
        # Get user emails (email is already in LoginLog)
        result = []
        for log in logs:
            result.append({
                "logId": log.log_id,
                "userId": log.user_id,
                "email": log.email,
                "loginTime": log.attempted_at.isoformat() if log.attempted_at else None,
                "ipAddress": log.ip_address,
                "isSuccessful": log.is_successful,
                "failureReason": log.failure_reason
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching login logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch login logs: {str(e)}")

# ==================== User Management Endpoints ====================

@router.get("/users/{user_id}", response_model=UserOut, summary="Get a user by ID")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a single user by ID (admin only)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.delete("/users/{user_id}", summary="Delete a user")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user by ID (admin only)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting admin
        if user.email == "admin@admin.com":
            raise HTTPException(status_code=403, detail="Cannot delete admin user")
        
        # Delete related login logs first (cascade delete)
        from app.db.models.login_log import LoginLog
        db.query(LoginLog).filter(LoginLog.user_id == user_id).delete(synchronize_session=False)
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully", "userId": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.put("/users/{user_id}", response_model=UserOut, summary="Update a user")
def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user information (admin only)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if user_data.firstName is not None:
            user.first_name = user_data.firstName
        if user_data.lastName is not None:
            user.last_name = user_data.lastName
        if user_data.email is not None:
            # Check if email already exists
            existing = db.query(User).filter(User.email == user_data.email, User.user_id != user_id).first()
            if existing:
                raise HTTPException(status_code=409, detail="Email already in use")
            user.email = user_data.email
        
        db.commit()
        db.refresh(user)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.post("/users", response_model=UserOut, summary="Create a new user")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (admin only)"""
    try:
        # Check if email already exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# ==================== Product Management Endpoints ====================
# Note: Products are managed in a separate database with complex structure
# For admin dashboard, we'll provide basic CRUD on the products table only

from app.db.session import ProductsSessionLocal, products_engine

# Lazily reflect products table
_products_table_loaded = False
ProductsTable = None

def _ensure_products_table():
    global _products_table_loaded, ProductsTable
    if not _products_table_loaded:
        from sqlalchemy import MetaData, Table
        metadata = MetaData()
        ProductsTable = Table("products", metadata, autoload_with=products_engine)
        _products_table_loaded = True

class ProductCreate(BaseModel):
    productName: str
    categoryName: str = None
    description: str = None
    basePrice: float = None

class ProductUpdate(BaseModel):
    productName: str = None
    categoryName: str = None
    description: str = None
    basePrice: float = None

@router.get("/products/{product_id}", summary="Get a product by ID")
def get_product(product_id: int):
    """Get a single product by ID (admin only)"""
    try:
        _ensure_products_table()
        with ProductsSessionLocal() as db:
            from sqlalchemy import select
            query = select(ProductsTable).where(ProductsTable.c.productId == product_id)
            result = db.execute(query).first()
            
            if not result:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {
                "productId": result.productId,
                "productName": result.productName,
                "categoryName": result.categoryName,
                "description": result.description,
                "basePrice": float(result.basePrice) if result.basePrice else None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

@router.delete("/products/{product_id}", summary="Delete a product")
def delete_product(product_id: int):
    """Delete a product by ID (admin only)"""
    try:
        _ensure_products_table()
        with ProductsSessionLocal() as db:
            from sqlalchemy import delete
            query = delete(ProductsTable).where(ProductsTable.c.productId == product_id)
            result = db.execute(query)
            db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {"message": "Product deleted successfully", "productId": product_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")

@router.put("/products/{product_id}", summary="Update a product")
def update_product(product_id: int, product_data: ProductUpdate):
    """Update product information (admin only)"""
    try:
        _ensure_products_table()
        with ProductsSessionLocal() as db:
            from sqlalchemy import update
            
            # Build update dict with only provided fields
            update_dict = {}
            if product_data.productName is not None:
                update_dict['productName'] = product_data.productName
            if product_data.categoryName is not None:
                update_dict['categoryName'] = product_data.categoryName
            if product_data.description is not None:
                update_dict['description'] = product_data.description
            if product_data.basePrice is not None:
                update_dict['basePrice'] = product_data.basePrice
            
            if not update_dict:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            query = update(ProductsTable).where(ProductsTable.c.productId == product_id).values(**update_dict)
            result = db.execute(query)
            db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Fetch updated product
            from sqlalchemy import select
            query = select(ProductsTable).where(ProductsTable.c.productId == product_id)
            updated = db.execute(query).first()
            
            return {
                "productId": updated.productId,
                "productName": updated.productName,
                "categoryName": updated.categoryName,
                "description": updated.description,
                "basePrice": float(updated.basePrice) if updated.basePrice else None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")

@router.post("/products", summary="Create a new product")
def create_product(product_data: ProductCreate):
    """Create a new product (admin only)"""
    try:
        _ensure_products_table()
        with ProductsSessionLocal() as db:
            from sqlalchemy import insert, select
            
            insert_dict = {
                'productName': product_data.productName,
                'categoryName': product_data.categoryName,
                'description': product_data.description,
                'basePrice': product_data.basePrice
            }
            
            query = insert(ProductsTable).values(**insert_dict)
            result = db.execute(query)
            db.commit()
            
            # Fetch created product
            new_id = result.inserted_primary_key[0]
            query = select(ProductsTable).where(ProductsTable.c.productId == new_id)
            created = db.execute(query).first()
            
            return {
                "productId": created.productId,
                "productName": created.productName,
                "categoryName": created.categoryName,
                "description": created.description,
                "basePrice": float(created.basePrice) if created.basePrice else None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")
