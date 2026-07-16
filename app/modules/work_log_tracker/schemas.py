from datetime import date,datetime,time
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
Mode=Literal["timed","manual"];Status=Literal["planned","in_progress","completed","paused","cancelled"];Period=Literal["all","today","week","month","past"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class ProjectWrite(BaseModel):
 name:str=Field(min_length=1,max_length=120);code:str|None=Field(None,max_length=30);client_name:str|None=Field(None,alias="clientName",max_length=120);description:str|None=Field(None,max_length=3000);default_billable:bool=Field(False,alias="defaultBillable");is_active:bool=Field(True,alias="isActive");model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","code","client_name","description",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class ProjectCreate(ProjectWrite):pass
class ProjectUpdate(ProjectWrite):pass
class LogWrite(BaseModel):
 project_id:str=Field(alias="projectId",min_length=1,max_length=36);title:str=Field(min_length=1,max_length=180);work_date:date=Field(alias="workDate");start_time:time|None=Field(None,alias="startTime");end_time:time|None=Field(None,alias="endTime");manual_duration_minutes:int|None=Field(None,alias="manualDurationMinutes",ge=1,le=1440);break_minutes:int=Field(0,alias="breakMinutes",ge=0,le=1439);entry_mode:Mode=Field(alias="entryMode");status:Status="completed";is_billable:bool=Field(False,alias="isBillable");accomplishments:str|None=Field(None,max_length=5000);blockers:str|None=Field(None,max_length=5000);notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","accomplishments","blockers","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @model_validator(mode="after")
 def mode_fields(self):
  if self.entry_mode=="timed" and (not self.start_time or not self.end_time):raise ValueError("Timed entries require start and end times.")
  if self.entry_mode=="manual" and not self.manual_duration_minutes:raise ValueError("Manual entries require a positive duration.")
  return self
class LogCreate(LogWrite):pass
class LogUpdate(LogWrite):pass
class ProjectResponse(ProjectWrite):
 id:str;log_count:int=Field(serialization_alias="logCount");logged_minutes:int=Field(serialization_alias="loggedMinutes");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(from_attributes=True,populate_by_name=True)
class LogResponse(LogWrite):
 id:str;project_name:str=Field(serialization_alias="projectName");duration_minutes:int=Field(serialization_alias="durationMinutes");is_overnight:bool=Field(serialization_alias="isOvernight");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(from_attributes=True,populate_by_name=True)
class LogList(BaseModel):items:list[LogResponse];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class Dashboard(BaseModel):today_minutes:int=Field(serialization_alias="todayMinutes");week_minutes:int=Field(serialization_alias="weekMinutes");month_minutes:int=Field(serialization_alias="monthMinutes");completed_logs:int=Field(serialization_alias="completedLogs");in_progress_logs:int=Field(serialization_alias="inProgressLogs");billable_minutes:int=Field(serialization_alias="billableMinutes");non_billable_minutes:int=Field(serialization_alias="nonBillableMinutes");active_projects:int=Field(serialization_alias="activeProjects")
