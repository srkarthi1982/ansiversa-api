from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
from .constants import ASSET_CATEGORIES,LIABILITY_CATEGORIES
AccountType=Literal["asset","liability"];Status=Literal["active","archived"]
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class AccountWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);account_type:AccountType=Field(alias="accountType");category:str=Field(max_length=30);currency_code:str=Field("USD",alias="currencyCode",pattern=r"^[A-Z]{3}$");institution_name:str|None=Field(None,alias="institutionName",max_length=180);current_balance:Decimal=Field(alias="currentBalance",ge=0,max_digits=16,decimal_places=2);valuation_date:date=Field(alias="valuationDate");include_in_net_worth:bool=Field(True,alias="includeInNetWorth");status:Status="active";notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","institution_name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("currency_code",mode="before")
 @classmethod
 def currency(c,v):return str(v).strip().upper()
 @model_validator(mode="after")
 def compatible(self):
  allowed=ASSET_CATEGORIES if self.account_type=="asset" else LIABILITY_CATEGORIES
  if self.category not in allowed:raise ValueError("Category is incompatible with account type.")
  return self
class AccountCreate(AccountWrite):pass
class AccountUpdate(AccountWrite):pass
class BalanceWrite(BaseModel):
 balance_date:date=Field(alias="balanceDate");balance_amount:Decimal=Field(alias="balanceAmount",ge=0,max_digits=16,decimal_places=2);change_reason:str|None=Field(None,alias="changeReason",max_length=180);notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("change_reason","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class BalanceCreate(BalanceWrite):pass
class BalanceUpdate(BalanceWrite):pass
class SnapshotCreate(BaseModel):
 snapshot_date:date=Field(alias="snapshotDate");name:str=Field(min_length=1,max_length=180);notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class BalanceResponse(BalanceWrite):id:str;change:Decimal|None;is_latest:bool=Field(serialization_alias="isLatest");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class AccountSummary(AccountWrite):id:str;entry_count:int=Field(serialization_alias="entryCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class AccountDetail(AccountSummary):entries:list[BalanceResponse]
class AccountList(BaseModel):items:list[AccountSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class CurrencyTotal(BaseModel):currency_code:str=Field(serialization_alias="currencyCode");assets:Decimal;liabilities:Decimal;net_worth:Decimal=Field(serialization_alias="netWorth")
class SnapshotItemResponse(BaseModel):id:str;account_id:str|None=Field(serialization_alias="accountId");account_name:str=Field(serialization_alias="accountName");account_type:str=Field(serialization_alias="accountType");category:str;currency_code:str=Field(serialization_alias="currencyCode");balance_amount:Decimal=Field(serialization_alias="balanceAmount");included:bool;model_config=ConfigDict(populate_by_name=True)
class SnapshotSummary(BaseModel):id:str;snapshot_date:date=Field(serialization_alias="snapshotDate");name:str;notes:str|None;account_count:int=Field(serialization_alias="accountCount");totals:list[CurrencyTotal];created_at:datetime=Field(serialization_alias="createdAt");model_config=ConfigDict(populate_by_name=True)
class SnapshotDetail(SnapshotSummary):items:list[SnapshotItemResponse]
class SnapshotList(BaseModel):items:list[SnapshotSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class ChangeTotal(CurrencyTotal):asset_difference:Decimal=Field(serialization_alias="assetDifference");liability_difference:Decimal=Field(serialization_alias="liabilityDifference");net_worth_difference:Decimal=Field(serialization_alias="netWorthDifference");percentage_change:Decimal|None=Field(serialization_alias="percentageChange")
class Comparison(BaseModel):previous:SnapshotSummary;current:SnapshotSummary;currencies:list[ChangeTotal];warning:str|None
class Dashboard(BaseModel):active_assets:int=Field(serialization_alias="activeAssets");active_liabilities:int=Field(serialization_alias="activeLiabilities");archived_accounts:int=Field(serialization_alias="archivedAccounts");excluded_accounts:int=Field(serialization_alias="excludedAccounts");totals:list[CurrencyTotal];latest_snapshot_date:date|None=Field(serialization_alias="latestSnapshotDate");recent_accounts:list[AccountSummary]=Field(serialization_alias="recentAccounts")
