from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ArchiveFilter = Literal["active", "archived", "all"]
WarrantyFilter = Literal["all", "expiring", "expired", "noWarranty"]
ItemSort = Literal["purchaseDate", "estimatedValue", "title"]
WarrantyStatus = Literal["active", "expiringSoon", "expired", "noWarranty"]
Condition = Literal["New", "Good", "Fair", "Needs Repair", "Damaged"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class InventoryCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)


class InventoryCategoryUpdateRequest(InventoryCategoryCreateRequest):
    pass


class InventoryCategoryResponse(BaseModel):
    id: str
    name: str
    item_count: int = Field(serialization_alias="itemCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class InventoryItemCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    room: str = Field(min_length=1, max_length=120)
    quantity: int = Field(default=1, ge=1, le=9999)
    purchase_date: str | None = Field(default=None, alias="purchaseDate", max_length=40)
    purchase_price: Decimal | None = Field(default=None, alias="purchasePrice", ge=0, max_digits=12, decimal_places=2)
    estimated_value: Decimal | None = Field(default=None, alias="estimatedValue", ge=0, max_digits=12, decimal_places=2)
    warranty_expiry: str | None = Field(default=None, alias="warrantyExpiry", max_length=40)
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, alias="serialNumber", max_length=160)
    condition: Condition = "Good"
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "room", "purchase_date", "warranty_expiry", "brand", "model", "serial_number", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "InventoryItemCreateRequest":
        _validate_iso_date(self.purchase_date, "purchaseDate")
        _validate_iso_date(self.warranty_expiry, "warrantyExpiry")
        return self


class InventoryItemUpdateRequest(InventoryItemCreateRequest):
    pass


class InventoryItemSummaryResponse(BaseModel):
    id: str
    title: str
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    room: str
    quantity: int
    purchase_date: str | None = Field(serialization_alias="purchaseDate")
    purchase_price: Decimal | None = Field(serialization_alias="purchasePrice")
    estimated_value: Decimal | None = Field(serialization_alias="estimatedValue")
    warranty_expiry: str | None = Field(serialization_alias="warrantyExpiry")
    warranty_status: WarrantyStatus = Field(serialization_alias="warrantyStatus")
    days_until_warranty_expiry: int | None = Field(serialization_alias="daysUntilWarrantyExpiry")
    brand: str | None
    model: str | None
    serial_number: str | None = Field(serialization_alias="serialNumber")
    condition: Condition
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    archived: bool
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class InventoryItemDetailResponse(InventoryItemSummaryResponse):
    notes: str | None


class InventoryCountItem(BaseModel):
    label: str
    count: int


class InventoryValueItem(BaseModel):
    label: str
    value: Decimal


class InventoryDashboardResponse(BaseModel):
    total_items: int = Field(serialization_alias="totalItems")
    active_items: int = Field(serialization_alias="activeItems")
    archived_items: int = Field(serialization_alias="archivedItems")
    warranty_expiring_count: int = Field(serialization_alias="warrantyExpiringCount")
    estimated_total_value: Decimal = Field(serialization_alias="estimatedTotalValue")


class InventoryInsightsResponse(InventoryDashboardResponse):
    categories: list[InventoryCategoryResponse]
    category_distribution: list[InventoryCountItem] = Field(serialization_alias="categoryDistribution")
    room_distribution: list[InventoryCountItem] = Field(serialization_alias="roomDistribution")
    condition_distribution: list[InventoryCountItem] = Field(serialization_alias="conditionDistribution")
    warranty_summary: list[InventoryCountItem] = Field(serialization_alias="warrantySummary")
    recent_items: list[InventoryItemSummaryResponse] = Field(serialization_alias="recentItems")
    highest_value_items: list[InventoryItemSummaryResponse] = Field(serialization_alias="highestValueItems")


def _validate_iso_date(value: str | None, field_name: str) -> None:
    if not value:
        return
    from datetime import date

    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc
