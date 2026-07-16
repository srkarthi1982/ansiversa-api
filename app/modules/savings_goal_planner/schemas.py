import re
from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
Category=Literal["emergency","travel","education","vehicle","home","wedding","family","purchase","project","other"];Priority=Literal["low","medium","high"];Status=Literal["active","paused","completed","cancelled","archived"];TxType=Literal["contribution","withdrawal","adjustment_increase","adjustment_decrease"];Period=Literal["all","due_soon","overdue","completed"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class GoalWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);description:str|None=Field(None,max_length=5000);category:Category="other";currency_code:str=Field("USD",alias="currencyCode",pattern=r"^[A-Z]{3}$");target_amount:Decimal=Field(alias="targetAmount",gt=0,max_digits=14,decimal_places=2);starting_amount:Decimal=Field(Decimal("0.00"),alias="startingAmount",ge=0,max_digits=14,decimal_places=2);target_date:date|None=Field(None,alias="targetDate");priority:Priority="medium";status:Status="active";notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","description","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("currency_code",mode="before")
 @classmethod
 def currency(c,v):return str(v).strip().upper()
 @model_validator(mode="after")
 def amounts(self):
  if self.starting_amount>self.target_amount:raise ValueError("Starting amount cannot exceed target amount.")
  return self
class GoalCreate(GoalWrite):pass
class GoalUpdate(GoalWrite):pass
class TransactionWrite(BaseModel):
 transaction_date:date=Field(alias="transactionDate");transaction_type:TxType=Field(alias="transactionType");amount:Decimal=Field(gt=0,max_digits=14,decimal_places=2);description:str|None=Field(None,max_length=300);notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("description","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class TransactionCreate(TransactionWrite):pass
class TransactionUpdate(TransactionWrite):pass
class MilestoneWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);target_amount:Decimal=Field(alias="targetAmount",gt=0,max_digits=14,decimal_places=2);target_date:date|None=Field(None,alias="targetDate");status:Literal["pending","cancelled"]="pending";notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class MilestoneCreate(MilestoneWrite):pass
class MilestoneUpdate(MilestoneWrite):pass
class TransactionResponse(TransactionWrite):id:str;created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class MilestoneResponse(MilestoneWrite):id:str;status:str;sort_order:int=Field(serialization_alias="sortOrder");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class GoalSummary(GoalWrite):
 id:str;current_amount:Decimal=Field(serialization_alias="currentAmount");remaining_amount:Decimal=Field(serialization_alias="remainingAmount");progress_percent:Decimal=Field(serialization_alias="progressPercent");days_remaining:int|None=Field(serialization_alias="daysRemaining");months_remaining:Decimal|None=Field(serialization_alias="monthsRemaining");required_weekly:Decimal=Field(serialization_alias="requiredWeekly");required_monthly:Decimal=Field(serialization_alias="requiredMonthly");is_overdue:bool=Field(serialization_alias="isOverdue");is_due_soon:bool=Field(serialization_alias="isDueSoon");transaction_count:int=Field(serialization_alias="transactionCount");milestone_count:int=Field(serialization_alias="milestoneCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class GoalDetail(GoalSummary):transactions:list[TransactionResponse];milestones:list[MilestoneResponse];average_contribution:Decimal=Field(serialization_alias="averageContribution");last_contribution_date:date|None=Field(serialization_alias="lastContributionDate")
class GoalList(BaseModel):items:list[GoalSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class CurrencyTotal(BaseModel):currency_code:str=Field(serialization_alias="currencyCode");target_amount:Decimal=Field(serialization_alias="targetAmount");saved_amount:Decimal=Field(serialization_alias="savedAmount");remaining_amount:Decimal=Field(serialization_alias="remainingAmount")
class Dashboard(BaseModel):active_goals:int=Field(serialization_alias="activeGoals");completed_goals:int=Field(serialization_alias="completedGoals");due_soon_goals:int=Field(serialization_alias="dueSoonGoals");overdue_goals:int=Field(serialization_alias="overdueGoals");recent_contributions:int=Field(serialization_alias="recentContributions");currency_totals:list[CurrencyTotal]=Field(serialization_alias="currencyTotals")
