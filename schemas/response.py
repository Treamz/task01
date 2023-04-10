from pydantic import BaseModel



class Response(BaseModel): 
    status: int | str
    accs: list[str | int]
    message: str

