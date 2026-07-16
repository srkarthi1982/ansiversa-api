import re
from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
Status=Literal["draft","open","partially_settled","settled","cancelled"];Period=Literal["all","recent","month","past"];Split=Literal["equal","custom","single_participant"]
Money=Decimal
def clean(v):
 if isinstance(v,str):v=" ".join(v.strip().split());return v or None
 return v
class BillWrite(BaseModel):
 title:str=Field(min_length=1,max_length=180);bill_date:date=Field(alias="billDate");merchant_name:str|None=Field(None,alias="merchantName",max_length=180);currency_code:str=Field("USD",alias="currencyCode",pattern=r"^[A-Z]{3}$");discount_amount:Money=Field(Decimal("0.00"),alias="discountAmount",ge=0,max_digits=14,decimal_places=2);tax_amount:Money=Field(Decimal("0.00"),alias="taxAmount",ge=0,max_digits=14,decimal_places=2);service_charge_amount:Money=Field(Decimal("0.00"),alias="serviceChargeAmount",ge=0,max_digits=14,decimal_places=2);tip_amount:Money=Field(Decimal("0.00"),alias="tipAmount",ge=0,max_digits=14,decimal_places=2);status:Status="draft";notes:str|None=Field(None,max_length=5000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("title","merchant_name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("currency_code",mode="before")
 @classmethod
 def currency(c,v):return str(v).strip().upper()
class BillCreate(BillWrite):pass
class BillUpdate(BillWrite):pass
class ParticipantWrite(BaseModel):
 name:str=Field(min_length=1,max_length=120);email:str|None=Field(None,max_length=254);paid_amount:Money=Field(Decimal("0.00"),alias="paidAmount",ge=0,max_digits=14,decimal_places=2);notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","email","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
 @field_validator("email")
 @classmethod
 def email_valid(c,v):
  if v and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",v):raise ValueError("Enter a valid email address.")
  return v
class ParticipantCreate(ParticipantWrite):pass
class ParticipantUpdate(ParticipantWrite):pass
class ItemWrite(BaseModel):
 name:str=Field(min_length=1,max_length=180);quantity:Decimal=Field(gt=0,max_digits=12,decimal_places=2);unit_price:Money=Field(alias="unitPrice",ge=0,max_digits=14,decimal_places=2);split_method:Split=Field("equal",alias="splitMethod");notes:str|None=Field(None,max_length=3000);model_config=ConfigDict(extra="forbid",populate_by_name=True)
 @field_validator("name","notes",mode="before")
 @classmethod
 def tidy(c,v):return clean(v)
class ItemCreate(ItemWrite):pass
class ItemUpdate(ItemWrite):pass
class AllocationInput(BaseModel):participant_id:str=Field(alias="participantId");amount:Money|None=Field(None,ge=0,max_digits=14,decimal_places=2);model_config=ConfigDict(extra="forbid",populate_by_name=True)
class AllocationReplace(BaseModel):split_method:Split=Field(alias="splitMethod");allocations:list[AllocationInput]=Field(min_length=1);model_config=ConfigDict(extra="forbid",populate_by_name=True)
class AllocationResponse(BaseModel):id:str;participant_id:str=Field(serialization_alias="participantId");participant_name:str=Field(serialization_alias="participantName");amount:Money
class ParticipantResponse(ParticipantWrite):
 id:str;share_amount:Money=Field(serialization_alias="shareAmount");outstanding_amount:Money=Field(serialization_alias="outstandingAmount");settlement_status:str=Field(serialization_alias="settlementStatus");sort_order:int=Field(serialization_alias="sortOrder");model_config=ConfigDict(populate_by_name=True)
class ItemResponse(ItemWrite):
 id:str;line_total:Money=Field(serialization_alias="lineTotal");sort_order:int=Field(serialization_alias="sortOrder");allocations:list[AllocationResponse];allocated_amount:Money=Field(serialization_alias="allocatedAmount");model_config=ConfigDict(populate_by_name=True)
class BillSummary(BillWrite):
 id:str;subtotal_amount:Money=Field(serialization_alias="subtotalAmount");total_amount:Money=Field(serialization_alias="totalAmount");outstanding_amount:Money=Field(serialization_alias="outstandingAmount");participant_count:int=Field(serialization_alias="participantCount");item_count:int=Field(serialization_alias="itemCount");created_at:datetime=Field(serialization_alias="createdAt");updated_at:datetime=Field(serialization_alias="updatedAt");model_config=ConfigDict(populate_by_name=True)
class BillDetail(BillSummary):participants:list[ParticipantResponse];items:list[ItemResponse];is_fully_allocated:bool=Field(serialization_alias="isFullyAllocated")
class BillList(BaseModel):items:list[BillSummary];total:int;page:int;page_size:int=Field(serialization_alias="pageSize");pages:int
class Dashboard(BaseModel):total_bills:int=Field(serialization_alias="totalBills");open_bills:int=Field(serialization_alias="openBills");settled_bills:int=Field(serialization_alias="settledBills");outstanding_amount:Money=Field(serialization_alias="outstandingAmount");recorded_value:Money=Field(serialization_alias="recordedValue")
