# BaseRepository for FastAPI with SQLAlchemy and Pagination

A generic repository class designed to simplify CRUD operations and querying with SQLAlchemy and FastAPI. It supports:

- **Create, Read, Update, and Delete (CRUD)** operations.
- **Filtering, searching, and sorting** records.
- **Pagination** with [fastapi-pagination](https://fastapi-pagination.timonweb.com/).

---

## Features

1. **Create**: Add new records to the database.
2. **Read**: Retrieve single or multiple records with optional relations.
3. **Update**: Modify existing records by their ID.
4. **Delete**: Remove records by their ID.
5. **Index**: Perform advanced queries with filtering, searching, sorting, and pagination.

---

## Installation

Install the required dependencies:

```bash
pip install fastapi sqlalchemy sqlalchemy[asyncio] fastapi-pagination
```
## Usage

### Prerequisites

- Your SQLAlchemy models should inherit from **`DeclarativeMeta`**.
- The database session must be an instance of **`AsyncSession`**.

## Setting Up
### Define your SQLAlchemy model:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
```

### Define your Pydantic schema:

```python
from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True
```
 

```python
from fastapi import Depends , APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from your_project.database import get_db  # Your database session dependency
from your_project.repositories import BaseRepository
from your_project.models import User, UserSchema
from fastapi import APIRouter

router = APIRouter()

@router.post("/users/", response_model=UserSchema)
async def create_user(
    user: UserSchema, 
    db: AsyncSession = Depends(get_db)
):
    user_repo = BaseRepository[User, UserSchema](User, db)
    return await user_repo.create(user)

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db)
):
    user_repo = BaseRepository[User, UserSchema](User, db)
    return await user_repo.get(user_id)

```

### Methods Examples

## create
### Creates a new record in the database.
```python 
async def create(self, schema: SchemaType) -> ModelType
```
## delete
### Deletes a record by its ID.
```python
async def delete(self, record_id: int) -> bool
```
## index
### Retrieves records with filtering, sorting, searching, and pagination.

``` python
async def index(
    self,
    params: Params,
    filters: Optional[Dict[str, Any]] = None,
    search_fields: Optional[list[str]] = None,
    search_query: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_order: str = "desc",
    load_relations: list[str] = None
) -> Page[ModelType]
```






