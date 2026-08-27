from pydantic import BaseModel

#--------------------------------
#async def upload_document
#--------------------------------
class DocUploaderRequest(BaseModel):
    file_name: str