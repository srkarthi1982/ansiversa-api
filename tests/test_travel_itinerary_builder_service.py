import unittest
from datetime import date, time, timedelta
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.travel_itinerary_builder.db import Base
from app.modules.travel_itinerary_builder.schemas import (
    ActivityCreate,
    ItineraryCreate,
    ItineraryDayCreate,
    TravelCategoryCreate,
)
from app.modules.travel_itinerary_builder.service import (
    dashboard,
    delete_activity,
    delete_category,
    delete_day,
    delete_itinerary,
    get_itinerary,
    list_categories,
    list_itineraries,
    save_activity,
    save_category,
    save_day,
    save_itinerary,
)


class TravelItineraryBuilderTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.a = SimpleNamespace(id="a")
        self.b = SimpleNamespace(id="b")
        self.category = save_category(
            self.db,
            self.a,
            TravelCategoryCreate(name="Sightseeing", color="blue", sortOrder=1),
        )

    def tearDown(self):
        self.db.close()

    def make_trip(self, **overrides):
        payload = {
            "name": "Dubai Weekend",
            "destination": "Dubai",
            "startDate": date.today() + timedelta(days=10),
            "endDate": date.today() + timedelta(days=12),
            "status": "planned",
            "purpose": "Family",
            "notes": "Keep bookings together.",
        }
        payload.update(overrides)
        return save_itinerary(self.db, self.a, ItineraryCreate(**payload))

    def test_itinerary_validation_ownership_filters_and_summary_contract(self):
        with self.assertRaises(ValidationError):
            ItineraryCreate(
                name="Bad range",
                destination="Dubai",
                startDate=date.today(),
                endDate=date.today() - timedelta(days=1),
            )
        trip = self.make_trip()
        with self.assertRaises(HTTPException):
            self.make_trip(name=" dubai weekend ")
        with self.assertRaises(HTTPException):
            get_itinerary(self.db, self.b, trip.id)
        result = list_itineraries(
            self.db,
            self.a,
            q="weekend",
            status="planned",
            destination="dub",
            starts_from=date.today(),
            starts_to=date.today() + timedelta(days=20),
            page=1,
            page_size=5,
        )
        self.assertEqual(result.total, 1)
        self.assertNotIn("notes", result.items[0].model_dump())
        with self.assertRaises(HTTPException):
            list_itineraries(
                self.db,
                self.a,
                starts_from=date.today(),
                starts_to=date.today() - timedelta(days=1),
            )
        stats = dashboard(self.db, self.a)
        self.assertEqual(stats.planned, 1)
        self.assertEqual(stats.upcoming, 1)

    def test_days_activities_category_rules_and_cascades(self):
        trip = self.make_trip()
        with self.assertRaises(HTTPException):
            save_day(
                self.db,
                self.a,
                trip.id,
                ItineraryDayCreate(dayDate=trip.start_date - timedelta(days=1)),
            )
        trip = save_day(
            self.db,
            self.a,
            trip.id,
            ItineraryDayCreate(dayDate=trip.start_date, title="Arrival", notes="Check in."),
        )
        day = trip.days[0]
        with self.assertRaises(HTTPException):
            save_day(
                self.db,
                self.a,
                trip.id,
                ItineraryDayCreate(dayDate=day.day_date, title="Duplicate"),
            )
        with self.assertRaises(HTTPException):
            save_activity(
                self.db,
                self.a,
                trip.id,
                day.id,
                ActivityCreate(title="Dinner", startTime=time(20, 0), endTime=time(19, 0)),
            )
        trip = save_activity(
            self.db,
            self.a,
            trip.id,
            day.id,
            ActivityCreate(
                title="Museum",
                categoryId=self.category.id,
                startTime=time(10, 0),
                endTime=time(12, 0),
                location="Old Town",
                bookingReference="REF-1",
            ),
        )
        self.assertEqual(trip.activity_count, 1)
        activity = trip.days[0].activities[0]
        with self.assertRaises(HTTPException):
            save_activity(
                self.db,
                self.a,
                trip.id,
                day.id,
                ActivityCreate(title=" museum ", startTime=time(10, 0)),
            )
        with self.assertRaises(HTTPException):
            delete_category(self.db, self.a, self.category.id)
        trip = delete_activity(self.db, self.a, trip.id, day.id, activity.id)
        self.assertEqual(trip.activity_count, 0)
        delete_category(self.db, self.a, self.category.id)
        self.assertEqual(list_categories(self.db, self.a).total, 0)
        delete_day(self.db, self.a, trip.id, day.id)
        self.assertEqual(get_itinerary(self.db, self.a, trip.id).day_count, 0)
        delete_itinerary(self.db, self.a, trip.id)
        self.assertEqual(list_itineraries(self.db, self.a).total, 0)


if __name__ == "__main__":
    unittest.main()
