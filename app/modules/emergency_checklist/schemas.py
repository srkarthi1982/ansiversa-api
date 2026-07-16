from datetime import datetime
from pydantic import BaseModel,ConfigDict,Field,field_validator
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class CategoryWrite(BaseModel):
 name:str=Field(min_length=1,max_length=80);color:str|None=Field(None,max_length=40);sort_order:int=Field(0,alias="sortOrder",ge=0,le=10000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","color",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class EmergencyCategoryCreate(CategoryWrite):pass
class EmergencyCategoryUpdate(CategoryWrite):pass
class EmergencyCategoryResponse(CategoryWrite):
 id:str;checklist_count:int=Field(serialization_alias="checklistCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class EmergencyCategoryList(BaseModel):items:list[EmergencyCategoryResponse];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class ChecklistWrite(BaseModel):
 title:str=Field(min_length=1,max_length=180);category_id:str|None=Field(None,alias="categoryId");description:str|None=Field(None,max_length=4000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","category_id","description",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class EmergencyChecklistCreate(ChecklistWrite):pass
class EmergencyChecklistUpdate(ChecklistWrite):pass
class ChecklistItemWrite(BaseModel):
 title:str=Field(min_length=1,max_length=180);notes:str|None=Field(None,max_length=4000);completed:bool=False;sort_order:int=Field(0,alias="sortOrder",ge=0,le=10000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class ChecklistItemCreate(ChecklistItemWrite):pass
class ChecklistItemUpdate(ChecklistItemWrite):pass
class ChecklistItemResponse(ChecklistItemWrite):
 id:str;checklist_id:str=Field(serialization_alias="checklistId");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class EmergencyChecklistSummary(ChecklistWrite):
 id:str;category_name:str|None=Field(serialization_alias="categoryName");category_color:str|None=Field(serialization_alias="categoryColor");archived:bool;total_items:int=Field(serialization_alias="totalItems");completed_items:int=Field(serialization_alias="completedItems");remaining_items:int=Field(serialization_alias="remainingItems");completion_percentage:int=Field(serialization_alias="completionPercentage");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class EmergencyChecklistDetail(EmergencyChecklistSummary):items:list[ChecklistItemResponse]
class EmergencyChecklistList(BaseModel):items:list[EmergencyChecklistSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class EmergencyDashboard(BaseModel):total_checklists:int=Field(serialization_alias="totalChecklists");archived:int;completed:int;incomplete:int;categories:int;recent:list[EmergencyChecklistSummary];model_config=ConfigDict(populate_by_name=True)
