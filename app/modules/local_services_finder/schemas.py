import re
from datetime import date,datetime
from pydantic import BaseModel,ConfigDict,Field,field_validator
PHONE=re.compile(r"^[0-9+() .-]{3,40}$")
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
 id:str;provider_count:int=Field(serialization_alias="providerCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class CategoryList(BaseModel):items:list[CategoryResponse];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class ProviderWrite(BaseModel):
 business_name:str=Field(alias="businessName",min_length=1,max_length=180);category_id:str|None=Field(None,alias="categoryId");contact_person:str|None=Field(None,alias="contactPerson",max_length=120);phone:str|None=Field(None,max_length=40);alternate_phone:str|None=Field(None,alias="alternatePhone",max_length=40);email:str|None=Field(None,max_length=180);website:str|None=Field(None,max_length=240);address:str|None=Field(None,max_length=4000);city:str|None=Field(None,max_length=120);area:str|None=Field(None,max_length=120);notes:str|None=Field(None,max_length=5000);rating:int|None=Field(None,ge=1,le=5);preferred:bool=False;last_contacted:date|None=Field(None,alias="lastContacted");model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("business_name","category_id","contact_person","phone","alternate_phone","email","website","address","city","area","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("phone","alternate_phone")
 @classmethod
 def phone_ok(c,v):
  if v and not PHONE.match(v):raise ValueError("Phone must contain only digits, spaces, +, -, parentheses, or dots.")
  return v
 @field_validator("email")
 @classmethod
 def email_ok(c,v):
  if v and ("@" not in v or "." not in v.rsplit("@",1)[-1]):raise ValueError("Email must be valid.")
  return v
 @field_validator("website")
 @classmethod
 def website_ok(c,v):
  if v and not (v.startswith("http://") or v.startswith("https://")):raise ValueError("Website must start with http:// or https://.")
  return v
class ProviderCreate(ProviderWrite):pass
class ProviderUpdate(ProviderWrite):pass
class ProviderSummary(BaseModel):
 id:str;business_name:str=Field(serialization_alias="businessName");category_id:str|None=Field(serialization_alias="categoryId");category_name:str|None=Field(serialization_alias="categoryName");category_color:str|None=Field(serialization_alias="categoryColor");contact_person:str|None=Field(serialization_alias="contactPerson");phone:str|None;address:str|None;city:str|None;area:str|None;notes:str|None;rating:int|None;preferred:bool;archived:bool;last_contacted:date|None=Field(serialization_alias="lastContacted");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class ProviderDetail(ProviderSummary):
 alternate_phone:str|None=Field(serialization_alias="alternatePhone");email:str|None;website:str|None
class ProviderList(BaseModel):items:list[ProviderSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class Dashboard(BaseModel):providers:int;preferred:int;archived:int;recently_contacted:int=Field(serialization_alias="recentlyContacted");categories:int;recent:list[ProviderSummary];model_config=ConfigDict(populate_by_name=True)
