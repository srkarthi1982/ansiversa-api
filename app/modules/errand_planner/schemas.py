from datetime import date,datetime
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator
Status=Literal["pending","in_progress","completed","archived","cancelled"];Priority=Literal["low","medium","high"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class CategoryWrite(BaseModel):
 name:str=Field(min_length=1,max_length=80);color:str|None=Field(None,max_length=40);sort_order:int=Field(0,alias="sortOrder",ge=0,le=10000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","color",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class CategoryCreate(CategoryWrite):pass
class CategoryUpdate(CategoryWrite):pass
class CategoryResponse(CategoryWrite):
 id:str;errand_count:int=Field(serialization_alias="errandCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class CategoryList(BaseModel):items:list[CategoryResponse];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class ErrandWrite(BaseModel):
 title:str=Field(min_length=1,max_length=180);description:str|None=Field(None,max_length=4000);category_id:str|None=Field(None,alias="categoryId");priority:Priority="medium";due_date:date|None=Field(None,alias="dueDate");estimated_minutes:int|None=Field(None,alias="estimatedMinutes",ge=1,le=1440);location:str|None=Field(None,max_length=240);status:Status="pending";notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","description","location","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class ErrandCreate(ErrandWrite):pass
class ErrandUpdate(ErrandWrite):pass
class ErrandSummary(BaseModel):
 id:str;title:str;category_id:str|None=Field(serialization_alias="categoryId");category_name:str|None=Field(serialization_alias="categoryName");category_color:str|None=Field(serialization_alias="categoryColor");priority:Priority;due_date:date|None=Field(serialization_alias="dueDate");estimated_minutes:int|None=Field(serialization_alias="estimatedMinutes");location:str|None;status:Status;is_overdue:bool=Field(serialization_alias="isOverdue");is_due_today:bool=Field(serialization_alias="isDueToday");is_due_soon:bool=Field(serialization_alias="isDueSoon");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");completed_at:datetime|None=Field(serialization_alias="completedAt");model_config=ConfigDict(populate_by_name=True)
class ErrandDetail(ErrandSummary):
 description:str|None;notes:str|None
class ErrandList(BaseModel):items:list[ErrandSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class Dashboard(BaseModel):pending:int;in_progress:int=Field(serialization_alias="inProgress");completed:int;overdue:int;due_today:int=Field(serialization_alias="dueToday");due_soon:int=Field(serialization_alias="dueSoon");archived:int;cancelled:int;total_active:int=Field(serialization_alias="totalActive");recent:list[ErrandSummary];model_config=ConfigDict(populate_by_name=True)
