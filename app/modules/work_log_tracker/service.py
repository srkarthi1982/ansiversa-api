from datetime import date,datetime,timedelta
from math import ceil
from fastapi import HTTPException
from sqlalchemy import func,or_,select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.modules.work_log_tracker.models import WorkLog,WorkProject
from app.modules.work_log_tracker.schemas import Dashboard,LogList,LogResponse,ProjectResponse
def owner(u):return str(u.id)
def missing(k):raise HTTPException(404,f"{k} not found.")
def project(db,o,id):return db.scalar(select(WorkProject).options(selectinload(WorkProject.logs)).where(WorkProject.id==id,WorkProject.owner_id==o))
def log(db,o,id):return db.scalar(select(WorkLog).options(selectinload(WorkLog.project)).where(WorkLog.id==id,WorkLog.owner_id==o))
def interval(d,a,b):
 x=datetime.combine(d,a);y=datetime.combine(d,b)
 if y<=x:y+=timedelta(days=1)
 return x,y
def minutes(p):
 if p.entry_mode=="manual":return p.manual_duration_minutes
 a,b=interval(p.work_date,p.start_time,p.end_time);gross=int((b-a).total_seconds()/60)
 if p.break_minutes>=gross:raise HTTPException(422,"Break must be shorter than elapsed work time.")
 return gross-p.break_minutes
def pr(x):return ProjectResponse(name=x.name,code=x.code,client_name=x.client_name,description=x.description,default_billable=x.default_billable,is_active=x.is_active,id=x.id,log_count=len(x.logs),logged_minutes=sum(l.duration_minutes for l in x.logs if l.status!="cancelled"),created_at=x.created_at,updated_at=x.updated_at)
def lr(x):return LogResponse(project_id=x.project_id,title=x.title,work_date=x.work_date,start_time=x.start_time,end_time=x.end_time,manual_duration_minutes=x.duration_minutes if x.entry_mode=="manual" else None,break_minutes=x.break_minutes,entry_mode=x.entry_mode,status=x.status,is_billable=x.is_billable,accomplishments=x.accomplishments,blockers=x.blockers,notes=x.notes,id=x.id,project_name=x.project.name,duration_minutes=x.duration_minutes,is_overnight=bool(x.entry_mode=="timed" and x.end_time<=x.start_time),created_at=x.created_at,updated_at=x.updated_at)
def list_projects(db,u):return[pr(x) for x in db.scalars(select(WorkProject).options(selectinload(WorkProject.logs)).where(WorkProject.owner_id==owner(u)).order_by(WorkProject.is_active.desc(),WorkProject.name))]
def save_project(db,u,p,id=None):
 x=project(db,owner(u),id) if id else WorkProject(owner_id=owner(u))
 if id and not x:missing("Project")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 try:db.commit()
 except IntegrityError:db.rollback();raise HTTPException(409,"A project with this name or code already exists.")
 return pr(project(db,owner(u),x.id))
def delete_project(db,u,id):
 x=project(db,owner(u),id)
 if not x:missing("Project")
 if x.logs:raise HTTPException(409,"Projects with work history cannot be deleted. Deactivate this project instead.")
 db.delete(x);db.commit()
def save_log(db,u,p,id=None):
 proj=project(db,owner(u),p.project_id)
 if not proj:missing("Project")
 if not proj.is_active and not id:raise HTTPException(409,"Inactive projects cannot be used for new logs.")
 if p.entry_mode=="timed" and p.status!="cancelled":
  a,b=interval(p.work_date,p.start_time,p.end_time)
  q=select(WorkLog).where(WorkLog.owner_id==owner(u),WorkLog.entry_mode=="timed",WorkLog.status!="cancelled")
  if id:q=q.where(WorkLog.id!=id)
  for other in db.scalars(q):
   oa,ob=interval(other.work_date,other.start_time,other.end_time)
   if a<ob and b>oa:raise HTTPException(409,"This timed entry overlaps another active timed log.")
 x=log(db,owner(u),id) if id else WorkLog(owner_id=owner(u))
 if id and not x:missing("Work log")
 d=p.model_dump(exclude={"manual_duration_minutes"});
 if p.entry_mode=="manual":d.update(start_time=None,end_time=None,break_minutes=0)
 for k,v in d.items():setattr(x,k,v)
 x.duration_minutes=minutes(p)
 if not id:db.add(x)
 db.commit();return lr(log(db,owner(u),x.id))
def get_log(db,u,id):
 x=log(db,owner(u),id)
 if not x:missing("Work log")
 return lr(x)
def delete_log(db,u,id):
 x=log(db,owner(u),id)
 if not x:missing("Work log")
 db.delete(x);db.commit()
def list_logs(db,u,q,project_id,status,mode,billable,period,date_from,date_to,page,size):
 if date_from and date_to and date_from>date_to:raise HTTPException(422,"From date must be on or before to date.")
 f=[WorkLog.owner_id==owner(u)]
 if q:
  term=f"%{q.strip()}%";f.append(or_(WorkLog.title.ilike(term),WorkLog.accomplishments.ilike(term),WorkLog.blockers.ilike(term),WorkLog.notes.ilike(term),WorkLog.project.has(WorkProject.name.ilike(term)),WorkLog.project.has(WorkProject.client_name.ilike(term))))
 if project_id:f.append(WorkLog.project_id==project_id)
 if status:f.append(WorkLog.status==status)
 if mode:f.append(WorkLog.entry_mode==mode)
 if billable is not None:f.append(WorkLog.is_billable==billable)
 today=date.today();week=today-timedelta(days=today.weekday())
 if period=="today":f.append(WorkLog.work_date==today)
 elif period=="week":f.extend([WorkLog.work_date>=week,WorkLog.work_date<=today])
 elif period=="month":f.extend([WorkLog.work_date>=today.replace(day=1),WorkLog.work_date<=today])
 elif period=="past":f.append(WorkLog.work_date<today)
 if date_from:f.append(WorkLog.work_date>=date_from)
 if date_to:f.append(WorkLog.work_date<=date_to)
 total=db.scalar(select(func.count(WorkLog.id)).where(*f))or 0;items=list(db.scalars(select(WorkLog).options(selectinload(WorkLog.project)).where(*f).order_by(WorkLog.work_date.desc(),WorkLog.created_at.desc()).offset((page-1)*size).limit(size)));return LogList(items=[lr(x)for x in items],total=total,page=page,page_size=size,pages=ceil(total/size)if total else 0)
def dashboard(db,u):
 items=list(db.scalars(select(WorkLog).where(WorkLog.owner_id==owner(u))));today=date.today();week=today-timedelta(days=today.weekday());month=today.replace(day=1);counted=[x for x in items if x.status not in{"planned","cancelled"}]
 return Dashboard(today_minutes=sum(x.duration_minutes for x in counted if x.work_date==today),week_minutes=sum(x.duration_minutes for x in counted if week<=x.work_date<=today),month_minutes=sum(x.duration_minutes for x in counted if month<=x.work_date<=today),completed_logs=sum(x.status=="completed" for x in items),in_progress_logs=sum(x.status=="in_progress" for x in items),billable_minutes=sum(x.duration_minutes for x in counted if x.is_billable),non_billable_minutes=sum(x.duration_minutes for x in counted if not x.is_billable),active_projects=db.scalar(select(func.count()).select_from(WorkProject).where(WorkProject.owner_id==owner(u),WorkProject.is_active))or 0)
