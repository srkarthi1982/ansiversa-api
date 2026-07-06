from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.meal_planner.db import MealPlannerBase


def _uuid() -> str:
    return str(uuid4())


class Recipe(MealPlannerBase):
    __tablename__ = "Recipes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prep_minutes: Mapped[int | None] = mapped_column("prepMinutes", Integer, nullable=True)
    cook_minutes: Mapped[int | None] = mapped_column("cookMinutes", Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    entries: Mapped[list["MealPlanEntry"]] = relationship(back_populates="recipe")


class MealPlan(MealPlannerBase):
    __tablename__ = "MealPlans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    week_start_date: Mapped[str] = mapped_column("weekStartDate", String(40), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    entries: Mapped[list["MealPlanEntry"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class MealPlanEntry(MealPlannerBase):
    __tablename__ = "MealPlanEntries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    plan_id: Mapped[str] = mapped_column("mealPlanId", String(36), ForeignKey("MealPlans.id"), index=True, nullable=False)
    recipe_id: Mapped[str | None] = mapped_column("recipeId", String(36), ForeignKey("Recipes.id"), index=True, nullable=True)
    entry_date: Mapped[str] = mapped_column("entryDate", String(40), index=True, nullable=False)
    meal_type: Mapped[str] = mapped_column("mealType", String(40), default="dinner", server_default="dinner", nullable=False)
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plan: Mapped[MealPlan] = relationship(back_populates="entries")
    recipe: Mapped[Recipe | None] = relationship(back_populates="entries")
