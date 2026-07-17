import unittest
from datetime import date
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.leave_planner.db import LeavePlannerBase
from app.modules.leave_planner.schemas import (
    LeavePlannerEntryCreateRequest,
    LeavePlannerTypeCreateRequest,
)
from app.modules.leave_planner.service import (
    create_type,
    dashboard,
    delete_type,
    duration,
    get_entry,
    list_entries,
    save_entry,
)


class LeavePlannerServiceTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        LeavePlannerBase.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.user = SimpleNamespace(id="user-a")
        self.other_user = SimpleNamespace(id="user-b")
        self.leave_type = create_type(
            self.db,
            self.user,
            LeavePlannerTypeCreateRequest(
                name="Annual Leave", annualAllowanceDays=2, carryForwardDays=0
            ),
        )

    def tearDown(self):
        self.db.close()

    def entry(self, **overrides):
        values = {
            "leaveTypeId": self.leave_type.id,
            "title": "Summer break",
            "startDate": "2026-07-20",
            "endDate": "2026-07-24",
            "dayType": "full_day",
            "status": "approved",
        }
        values.update(overrides)
        return LeavePlannerEntryCreateRequest(**values)

    def test_weekday_and_half_day_duration_rules(self):
        self.assertEqual(duration(date(2026, 7, 17), date(2026, 7, 20), "full_day"), 2)
        self.assertEqual(duration(date(2026, 7, 20), date(2026, 7, 20), "first_half"), 0.5)
        with self.assertRaises(HTTPException):
            duration(date(2026, 7, 18), date(2026, 7, 19), "full_day")
        with self.assertRaises(HTTPException):
            duration(date(2026, 7, 18), date(2026, 7, 18), "first_half")
        with self.assertRaises(ValidationError):
            self.entry(startDate="2026-07-21", endDate="2026-07-20")
        with self.assertRaises(ValidationError):
            self.entry(dayType="second_half", endDate="2026-07-21")

    def test_overlap_ownership_balance_and_safe_delete(self):
        created = save_entry(self.db, self.user, self.entry())
        self.assertEqual(created.duration_days, 5)
        self.assertEqual(dashboard(self.db, self.user).remaining_leave, -3)
        with self.assertRaises(HTTPException) as overlap:
            save_entry(
                self.db,
                self.user,
                self.entry(title="Overlap", startDate="2026-07-24", endDate="2026-07-27"),
            )
        self.assertEqual(overlap.exception.status_code, 409)
        with self.assertRaises(HTTPException) as hidden:
            get_entry(self.db, self.other_user, created.id)
        self.assertEqual(hidden.exception.status_code, 404)
        with self.assertRaises(HTTPException) as protected:
            delete_type(self.db, self.user, self.leave_type.id)
        self.assertEqual(protected.exception.status_code, 409)

    def test_cancelled_leave_does_not_block_a_new_entry(self):
        save_entry(self.db, self.user, self.entry(status="cancelled"))
        created = save_entry(self.db, self.user, self.entry(title="Replacement"))
        self.assertEqual(created.status, "approved")

    def test_opposite_half_days_do_not_overlap(self):
        save_entry(self.db, self.user, self.entry(title="Morning", startDate="2026-07-20", endDate="2026-07-20", dayType="first_half"))
        created = save_entry(self.db, self.user, self.entry(title="Afternoon", startDate="2026-07-20", endDate="2026-07-20", dayType="second_half"))
        self.assertEqual(created.duration_days, 0.5)

    def test_type_names_are_unique_without_case_sensitivity(self):
        with self.assertRaises(HTTPException) as duplicate:
            create_type(self.db, self.user, LeavePlannerTypeCreateRequest(name="annual leave"))
        self.assertEqual(duplicate.exception.status_code, 409)

    def test_status_balance_contract_and_search_filters(self):
        statuses = ["planned", "pending", "approved", "taken", "cancelled", "rejected"]
        dates = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07", "2026-08-10"]
        for status, leave_date in zip(statuses, dates, strict=True):
            save_entry(
                self.db,
                self.user,
                self.entry(
                    title=f"Status {status}",
                    startDate=leave_date,
                    endDate=leave_date,
                    status=status,
                    reason=f"Reason {status}",
                ),
            )
        summary = dashboard(self.db, self.user)
        self.assertEqual(summary.used_leave, 2)
        self.assertEqual(summary.planned_leave, 2)
        self.assertEqual(summary.remaining_leave, 0)
        approved = list_entries(self.db, self.user, "reason APPROVED", None, "approved", "all", None, None, 1, 20)
        self.assertEqual(approved.total, 1)
        self.assertEqual(approved.items[0].status, "approved")

    def test_month_year_and_leap_boundaries(self):
        self.assertEqual(duration(date(2028, 2, 28), date(2028, 3, 1), "full_day"), 3)
        self.assertEqual(duration(date(2027, 12, 31), date(2028, 1, 3), "full_day"), 2)


if __name__ == "__main__":
    unittest.main()
