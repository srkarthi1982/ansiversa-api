import re
from datetime import date,datetime,time
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator
Status=Literal["draft","scheduled","in_progress","completed","cancelled","missed"]; Period=Literal["all","upcoming","current","past"]; Color=Literal["blue","green","amber","violet","rose","slate"]
def clean(v):
    if isinstance(v,str): v=" ".join(v.strip().split()); return v or None
    return v
class TypeWrite(BaseModel):
    name:str=Field(min_length=1,max_length=120); code:str|None=Field(None,max_length=30); description:str|None=Field(None,max_length=3000); default_start_time:time=Field(alias="defaultStartTime"); default_end_time:time=Field(alias="defaultEndTime"); default_break_minutes:int=Field(0,alias="defaultBreakMinutes",ge=0,le=1439); color_key:Color=Field("blue",alias="colorKey"); is_active:bool=Field(True,alias="isActive"); model_config=ConfigDict(extra="forbid",populate_by_name=True)
    @field_validator("name","code","description",mode="before")
    @classmethod
    def tidy(cls,v): return clean(v)
class TypeCreate(TypeWrite): pass
class TypeUpdate(TypeWrite): pass
class MemberWrite(BaseModel):
    name:str=Field(min_length=1,max_length=120); email:str|None=Field(None,max_length=254); phone:str|None=Field(None,max_length=50); role:str|None=Field(None,max_length=100); notes:str|None=Field(None,max_length=3000); is_active:bool=Field(True,alias="isActive"); model_config=ConfigDict(extra="forbid",populate_by_name=True)
    @field_validator("name","email","phone","role","notes",mode="before")
    @classmethod
    def tidy(cls,v): return clean(v)
    @field_validator("email")
    @classmethod
    def email_format(cls,v):
        if v and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",v): raise ValueError("Enter a valid email address.")
        return v
class MemberCreate(MemberWrite): pass
class MemberUpdate(MemberWrite): pass
class ShiftWrite(BaseModel):
    shift_type_id:str=Field(alias="shiftTypeId",min_length=1,max_length=36); member_id:str|None=Field(None,alias="memberId",max_length=36); title:str=Field(min_length=1,max_length=180); shift_date:date=Field(alias="shiftDate"); start_time:time=Field(alias="startTime"); end_time:time=Field(alias="endTime"); break_minutes:int=Field(0,alias="breakMinutes",ge=0,le=1439); location:str|None=Field(None,max_length=250); status:Status="scheduled"; notes:str|None=Field(None,max_length=5000); model_config=ConfigDict(extra="forbid",populate_by_name=True)
    @field_validator("title","location","notes",mode="before")
    @classmethod
    def tidy(cls,v): return clean(v)
class ShiftCreate(ShiftWrite): pass
class ShiftUpdate(ShiftWrite): pass
class TypeResponse(TypeWrite):
    id:str; shift_count:int=Field(serialization_alias="shiftCount"); created_at:datetime=Field(serialization_alias="createdAt"); updated_at:datetime=Field(serialization_alias="updatedAt"); model_config=ConfigDict(from_attributes=True,populate_by_name=True)
class MemberResponse(MemberWrite):
    id:str; shift_count:int=Field(serialization_alias="shiftCount"); created_at:datetime=Field(serialization_alias="createdAt"); updated_at:datetime=Field(serialization_alias="updatedAt"); model_config=ConfigDict(from_attributes=True,populate_by_name=True)
class ShiftResponse(ShiftWrite):
    id:str; shift_type_name:str=Field(serialization_alias="shiftTypeName"); member_name:str|None=Field(serialization_alias="memberName"); duration_minutes:int=Field(serialization_alias="durationMinutes"); is_overnight:bool=Field(serialization_alias="isOvernight"); created_at:datetime=Field(serialization_alias="createdAt"); updated_at:datetime=Field(serialization_alias="updatedAt"); model_config=ConfigDict(from_attributes=True,populate_by_name=True)
class ShiftList(BaseModel): items:list[ShiftResponse]; total:int; page:int; page_size:int=Field(serialization_alias="pageSize"); pages:int
class Dashboard(BaseModel): total_shifts:int=Field(serialization_alias="totalShifts"); upcoming_shifts:int=Field(serialization_alias="upcomingShifts"); completed_shifts:int=Field(serialization_alias="completedShifts"); cancelled_shifts:int=Field(serialization_alias="cancelledShifts"); scheduled_hours:float=Field(serialization_alias="scheduledHours"); completed_hours:float=Field(serialization_alias="completedHours"); active_members:int=Field(serialization_alias="activeMembers")
