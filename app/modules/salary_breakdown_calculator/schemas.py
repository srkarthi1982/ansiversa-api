from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
Frequency=Literal["weekly","biweekly","semimonthly","monthly","quarterly","annual"];Status=Literal["draft","active","archived"];EarningType=Literal["allowance","bonus","commission","overtime","reimbursement","other"];DeductionType=Literal["retirement","insurance","loan","tax_estimate","benefit","voluntary","other"];Method=Literal["fixed_amount","percentage_of_base","percentage_of_gross"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class ScenarioWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);description:str|None=Field(None,max_length=5000);currency_code:str=Field("USD",alias="currencyCode",pattern=r"^[A-Z]{3}$");pay_frequency:Frequency=Field("monthly",alias="payFrequency");base_salary_amount:Decimal=Field(alias="baseSalaryAmount",ge=0,max_digits=14,decimal_places=2);base_salary_period:Frequency=Field("monthly",alias="baseSalaryPeriod");working_days_per_week:Decimal=Field(Decimal("5"),alias="workingDaysPerWeek",gt=0,le=7,max_digits=4,decimal_places=2);working_hours_per_week:Decimal=Field(Decimal("40"),alias="workingHoursPerWeek",gt=0,le=168,max_digits=5,decimal_places=2);status:Status="active";notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","description","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("currency_code",mode="before")
 @classmethod
 def currency(c,v):return str(v).strip().upper()
class ScenarioCreate(ScenarioWrite):pass
class ScenarioUpdate(ScenarioWrite):pass
class EarningWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);earning_type:EarningType=Field(alias="earningType");amount:Decimal=Field(ge=0,max_digits=14,decimal_places=2);frequency:Frequency="monthly";is_taxable:bool=Field(False,alias="isTaxable");is_recurring:bool=Field(True,alias="isRecurring");effective_date:date|None=Field(None,alias="effectiveDate");notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class EarningCreate(EarningWrite):pass
class EarningUpdate(EarningWrite):pass
class DeductionWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);deduction_type:DeductionType=Field(alias="deductionType");calculation_method:Method=Field(alias="calculationMethod");amount:Decimal|None=Field(None,ge=0,max_digits=14,decimal_places=2);percentage:Decimal|None=Field(None,ge=0,le=100,max_digits=7,decimal_places=4);frequency:Frequency="monthly";is_recurring:bool=Field(True,alias="isRecurring");effective_date:date|None=Field(None,alias="effectiveDate");notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @model_validator(mode="after")
 def compatible(self):
  if self.calculation_method=="fixed_amount" and (self.amount is None or self.percentage is not None):raise ValueError("Fixed deductions require amount and forbid percentage.")
  if self.calculation_method!="fixed_amount" and (self.percentage is None or self.amount is not None):raise ValueError("Percentage deductions require percentage and forbid amount.")
  return self
class DeductionCreate(DeductionWrite):pass
class DeductionUpdate(DeductionWrite):pass
class ComponentTotals(BaseModel):annual_amount:Decimal=Field(serialization_alias="annualAmount");monthly_amount:Decimal=Field(serialization_alias="monthlyAmount")
class EarningResponse(EarningWrite,ComponentTotals):id:str;sort_order:int=Field(serialization_alias="sortOrder");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class DeductionResponse(DeductionWrite,ComponentTotals):id:str;calculated_annual:Decimal=Field(serialization_alias="calculatedAnnual");calculated_monthly:Decimal=Field(serialization_alias="calculatedMonthly");sort_order:int=Field(serialization_alias="sortOrder");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class ScenarioSummary(ScenarioWrite):
 id:str;annual_base:Decimal=Field(serialization_alias="annualBase");monthly_base:Decimal=Field(serialization_alias="monthlyBase");weekly_base:Decimal=Field(serialization_alias="weeklyBase");period_base:Decimal=Field(serialization_alias="periodBase");recurring_earnings:Decimal=Field(serialization_alias="recurringEarnings");one_time_earnings:Decimal=Field(serialization_alias="oneTimeEarnings");recurring_gross:Decimal=Field(serialization_alias="recurringGross");recurring_deductions:Decimal=Field(serialization_alias="recurringDeductions");one_time_deductions:Decimal=Field(serialization_alias="oneTimeDeductions");recurring_net:Decimal=Field(serialization_alias="recurringNet");net_to_gross_percent:Decimal=Field(serialization_alias="netToGrossPercent");earning_count:int=Field(serialization_alias="earningCount");deduction_count:int=Field(serialization_alias="deductionCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class ScenarioDetail(ScenarioSummary):earnings:list[EarningResponse];deductions:list[DeductionResponse]
class ScenarioList(BaseModel):items:list[ScenarioSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class CurrencyTotal(BaseModel):currency_code:str=Field(serialization_alias="currencyCode");recurring_gross:Decimal=Field(serialization_alias="recurringGross");recurring_net:Decimal=Field(serialization_alias="recurringNet")
class FrequencyCount(BaseModel):frequency:str;count:int
class Dashboard(BaseModel):total_scenarios:int=Field(serialization_alias="totalScenarios");active_scenarios:int=Field(serialization_alias="activeScenarios");archived_scenarios:int=Field(serialization_alias="archivedScenarios");recent_scenarios:int=Field(serialization_alias="recentScenarios");currency_totals:list[CurrencyTotal]=Field(serialization_alias="currencyTotals");frequency_counts:list[FrequencyCount]=Field(serialization_alias="frequencyCounts")
class Comparison(BaseModel):left:ScenarioSummary;right:ScenarioSummary;currency_compatible:bool=Field(serialization_alias="currencyCompatible");warning:str|None;base_difference:Decimal|None=Field(serialization_alias="baseDifference");gross_difference:Decimal|None=Field(serialization_alias="grossDifference");deduction_difference:Decimal|None=Field(serialization_alias="deductionDifference");net_difference:Decimal|None=Field(serialization_alias="netDifference")

