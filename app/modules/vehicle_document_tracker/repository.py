from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.modules.vehicle_document_tracker.models import VehicleDocument, VehicleDocumentType, VehicleDocumentVehicle


def add(db: Session, item):
    db.add(item)
    return item


def delete(db: Session, item) -> None:
    db.delete(item)


def list_vehicles(db: Session, owner_id: str) -> list[VehicleDocumentVehicle]:
    return list(db.scalars(select(VehicleDocumentVehicle).where(VehicleDocumentVehicle.owner_id == owner_id).order_by(VehicleDocumentVehicle.archived, VehicleDocumentVehicle.vehicle_name)))


def get_vehicle(db: Session, item_id: str) -> VehicleDocumentVehicle | None:
    return db.get(VehicleDocumentVehicle, item_id)


def list_types(db: Session, owner_id: str) -> list[VehicleDocumentType]:
    return list(db.scalars(select(VehicleDocumentType).where(or_(VehicleDocumentType.owner_id == owner_id, VehicleDocumentType.is_system == True)).order_by(VehicleDocumentType.is_system.desc(), VehicleDocumentType.sort_order, VehicleDocumentType.name)))


def get_type(db: Session, item_id: str) -> VehicleDocumentType | None:
    return db.get(VehicleDocumentType, item_id)


def list_documents(db: Session, owner_id: str) -> list[VehicleDocument]:
    result = db.execute(select(VehicleDocument).options(joinedload(VehicleDocument.vehicle), joinedload(VehicleDocument.document_type)).where(VehicleDocument.owner_id == owner_id).order_by(VehicleDocument.expiry_date.asc().nullslast(), VehicleDocument.updated_at.desc()))
    return list(result.unique().scalars())


def get_document(db: Session, item_id: str) -> VehicleDocument | None:
    result = db.execute(select(VehicleDocument).options(joinedload(VehicleDocument.vehicle), joinedload(VehicleDocument.document_type)).where(VehicleDocument.id == item_id))
    return result.unique().scalars().first()


def count_documents_for_vehicle(db: Session, owner_id: str, vehicle_id: str) -> int:
    return db.scalar(select(func.count()).select_from(VehicleDocument).where(VehicleDocument.owner_id == owner_id, VehicleDocument.vehicle_id == vehicle_id)) or 0


def count_documents_for_type(db: Session, owner_id: str, type_id: str) -> int:
    return db.scalar(select(func.count()).select_from(VehicleDocument).where(VehicleDocument.owner_id == owner_id, VehicleDocument.document_type_id == type_id)) or 0
