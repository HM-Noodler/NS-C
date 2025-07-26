from typing import Generic, TypeVar, Optional, List, Any
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common async database operations."""
    
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get a record by its ID."""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: str) -> bool:
        """Delete a record by ID."""
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
            return True
        return False
    
    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[ModelType]:
        """Get a record by a specific field value."""
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name) == field_value)
        )
        return result.scalars().first()
    
    async def get_multiple_by_field(self, field_name: str, field_values: List[Any]) -> List[ModelType]:
        """Get multiple records by field values."""
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field_name).in_(field_values))
        )
        return result.scalars().all()