#python -m fastapi dev .\main.py
#python -m uvicorn server:api --reload
from typing import Optional, List
from enum import IntEnum
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

api = FastAPI()

class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class TodoBase(BaseModel): # Base class for Todo, có tất cả các trường, trừ todo_id vì nó không được gán cứng
    todo_name: str = Field(..., min_length=1, max_length=50, description="Name of the todo")
    todo_description: str = Field(..., description="Description of the todo")
    priority: Priority = Field(default=Priority.LOW, description="Priority of the todo")

class TodoCreate(TodoBase): # Class khi tạo Todo, không có todo_id
    pass

class Todo(TodoBase): # Class khi lấy Todo, có todo_id
    todo_id: int = Field(..., description="ID of the todo")

class TodoUpdate(BaseModel): # Class khi cập nhật Todo, không có todo_id
    todo_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the todo")
    todo_description: Optional[str] = Field(None, description="Description of the todo")
    priority: Optional[Priority] = Field(None, description="Priority of the todo")

all_todos = [
    Todo(todo_id=1, todo_name="Sports", todo_description="Go to the gym", priority=Priority.LOW),
    Todo(todo_id=2, todo_name="Work", todo_description="Finish the report", priority=Priority.HIGH),
    Todo(todo_id=3, todo_name="Study", todo_description="Read the book", priority=Priority.MEDIUM),
]

# GET, POST, PUT, DELETE
@api.get("/")
def index():
    return {"message": "Hello World"}

@api.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return todo
        
    raise HTTPException(status_code=404, detail="Todo not found")

# http://127.0.0.1:8000/todos?first_n=2
@api.get("/todos", response_model=List[Todo])
def get_todos(first_n :int = None):
    if first_n:
        return all_todos[:first_n]
    return all_todos

@api.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo_id = max([todo.todo_id for todo in all_todos]) + 1

    new_todo = Todo(
        todo_id=new_todo_id,
        todo_name=todo.todo_name,
        todo_description=todo.todo_description,
        priority=todo.priority
    )

    all_todos.append(new_todo)

    return new_todo

@api.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoUpdate):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            if updated_todo.todo_name is not None:
                todo.todo_name = updated_todo.todo_name
            if updated_todo.todo_description is not None:
                todo.todo_description = updated_todo.todo_description
            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority
            return todo
    
    raise HTTPException(status_code=404, detail="Todo not found")

@api.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            deleted_todo = all_todos.pop(index)
            return deleted_todo
    return {'error': 'Todo not found'}