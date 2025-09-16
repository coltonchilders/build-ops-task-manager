from pydantic import BaseModel


class ImportJobResponse(BaseModel):
    id: str
    status: str
    total_rows: int
    processed_rows: int
    errors: str

    class Config:
        orm_mode = True

