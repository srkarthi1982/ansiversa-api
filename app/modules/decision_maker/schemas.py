from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator
DecisionType=Literal["personal","career","purchase","travel","education","project","business","other"];Status=Literal["draft","evaluating","decided","revisiting","archived","cancelled"];Direction=Literal["higher_is_better","lower_is_better"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class DecisionWrite(BaseModel):
 title:str=Field(min_length=1,max_length=180);question:str=Field(min_length=1,max_length=3000);description:str|None=Field(None,max_length=5000);decision_type:DecisionType=Field("personal",alias="decisionType");rating_scale:Literal[5,10]=Field(5,alias="ratingScale");status:Status="draft";target_date:date|None=Field(None,alias="targetDate");selected_option_id:str|None=Field(None,alias="selectedOptionId");outcome:str|None=Field(None,max_length=5000);reflection:str|None=Field(None,max_length=5000);notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","question","description","outcome","reflection","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class DecisionCreate(DecisionWrite):pass
class DecisionUpdate(DecisionWrite):pass
class OptionWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);description:str|None=Field(None,max_length=3000);pros:str|None=Field(None,max_length=3000);cons:str|None=Field(None,max_length=3000);risks:str|None=Field(None,max_length=3000);assumptions:str|None=Field(None,max_length=3000);notes:str|None=Field(None,max_length=3000);is_active:bool=Field(True,alias="isActive");model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","description","pros","cons","risks","assumptions","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class OptionCreate(OptionWrite):pass
class OptionUpdate(OptionWrite):pass
class CriterionWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);description:str|None=Field(None,max_length=3000);weight:Decimal=Field(gt=0,max_digits=10,decimal_places=2);direction:Direction="higher_is_better";is_active:bool=Field(True,alias="isActive");model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","description",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class CriterionCreate(CriterionWrite):pass
class CriterionUpdate(CriterionWrite):pass
class RatingUpsert(BaseModel):option_id:str=Field(alias="optionId");criterion_id:str=Field(alias="criterionId");rating:int;notes:str|None=Field(None,max_length=2000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
class RatingMatrix(BaseModel):ratings:list[RatingUpsert]=Field(max_length=1000)
class RatingResponse(RatingUpsert):id:str;model_config=ConfigDict(populate_by_name=True)
class CriterionResponse(CriterionWrite):id:str;sort_order:int=Field(serialization_alias="sortOrder");normalized_weight:Decimal=Field(serialization_alias="normalizedWeight");model_config=ConfigDict(populate_by_name=True)
class Contribution(BaseModel):criterion_id:str=Field(serialization_alias="criterionId");rating:int;contribution:Decimal;model_config=ConfigDict(populate_by_name=True)
class OptionResponse(OptionWrite):id:str;sort_order:int=Field(serialization_alias="sortOrder");completion_percent:Decimal=Field(serialization_alias="completionPercent");score:Decimal|None;rank:int|None;is_tied:bool=Field(serialization_alias="isTied");contributions:list[Contribution];model_config=ConfigDict(populate_by_name=True)
class DecisionSummary(BaseModel):
 id:str;title:str;question:str;decision_type:DecisionType=Field(serialization_alias="decisionType");rating_scale:Literal[5,10]=Field(serialization_alias="ratingScale");status:Status;target_date:date|None=Field(serialization_alias="targetDate");option_count:int=Field(serialization_alias="optionCount");criterion_count:int=Field(serialization_alias="criterionCount");evaluation_complete:bool=Field(serialization_alias="evaluationComplete");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");decided_at:datetime|None=Field(serialization_alias="decidedAt");model_config=ConfigDict(populate_by_name=True)
class DecisionDetail(DecisionSummary):
 description:str|None;selected_option_id:str|None=Field(serialization_alias="selectedOptionId");outcome:str|None;reflection:str|None;notes:str|None;options:list[OptionResponse];criteria:list[CriterionResponse];ratings:list[RatingResponse];warning:str
class DecisionList(BaseModel):items:list[DecisionSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class Dashboard(BaseModel):total:int;draft:int;evaluating:int;decided:int;revisiting:int;archived:int;due_soon:int=Field(serialization_alias="dueSoon");overdue:int;recent:list[DecisionSummary];model_config=ConfigDict(populate_by_name=True)
