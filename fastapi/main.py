from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi import HTTPException
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ↓↓↓↓↓↓↓↓ CORS 설정 시작 ↓↓↓↓↓↓↓↓
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ↑↑↑↑↑↑↑↑ CORS 설정 끝 ↑↑↑↑↑↑↑↑

@app.get('/')
async def say_hello():
    return {'message':"My First API!"}

@app.get('/hello/{name}')
async def greet(name:str, repeat: int = 1):
    return {'greeting':f'Hello, {name}! '*repeat+'Nice to Meet You'}

@app.get('/bye/{name}')
async def farewell(name:str):
    return {'farewell':f'Bye, {name}! See You Again'}

@app.get('/items/')
async def read_items(start: int = 0, count: int = 10):
    return {'message':f'I will show you {count} items from number {start}'}

class Note(BaseModel):
    author : str
    message : str

@app.post('/notes/')
async def create_note(received_note: Note):
    print(f'Got a new message! Author: {received_note.author}, message: {received_note.message}')
    return {'status':'Got a new message successfully', 'author':received_note.author, 'message':received_note.message}

class BookReview(BaseModel):
    book_title: str
    reviewer_name: str
    rating: int

@app.post('/reviews/')
async def create_review(received_review: BookReview):
    return {f'{received_review.reviewer_name} gave rate {received_review.rating} to book \'{received_review.book_title}\'. Thank you for the review.'}

class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool = False

todo_databse: List[TodoItem] = []
next_todo_id: int = 1

class TodoCreateRequest(BaseModel):
    title: str
@app.post('/todos/', response_model=TodoItem)
async def create_new_todo(new_todo_data: TodoCreateRequest):
    global next_todo_id

    todo_to_add = TodoItem(
        id = next_todo_id,
        title = new_todo_data.title,
        completed = False
    )

    todo_databse.append(todo_to_add)

    next_todo_id += 1

    return todo_to_add

@app.get('/todos/', response_model=List[TodoItem])
async def get_all_todo_items():
    return todo_databse

@app.get('/todos/{todo_id}', response_model=List[TodoItem])
async def get_one_todo_itme(todo_id: int):
    for i in todo_databse:
        if i.id == todo_id:
            return i
        
    raise HTTPException(status_code=404, detail=f"Can't find To-do ID {todo_id}.")

class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

@app.put('/todos/{todo_id}', response_model=TodoItem)
async def update_one_todo_item(todo_id: int, todo_update_data: TodoUpdateRequest):
    found_todo_to_update = None
    for temp in todo_databse:
        if temp.id == todo_id:
            found_todo_to_update = temp
            break
    
    if found_todo_to_update == None:
        raise HTTPException(status_code=404, detail=f"Can't find To-do ID {todo_id} to update.")
    
    if todo_update_data.title is not None:
        found_todo_to_update.title = todo_update_data.title
    
    if todo_update_data.completed is not None:
        found_todo_to_update.completed = todo_update_data.completed

    return found_todo_to_update

class DeleteResponseMessage(BaseModel):
    message: str

@app.delete('/todos/{todo_id}', response_model=DeleteResponseMessage)
async def delete_one_todo_item(todo_id: int):
    index_to_delete = -1
    for idx, todo_in_db in enumerate(todo_databse):
        if todo_in_db.id == todo_id:
            index_to_delete = idx
    
    if index_to_delete == -1:
        raise HTTPException(status_code=404, detail=f"Can't find To-do ID {todo_id} to delete.")
    
    todo_databse.pop(index_to_delete)

    return {"message": f"Successfully deleted to-do ID {todo_id}."}