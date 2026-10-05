import unittest
from unittest.mock import patch

from fastapi import HTTPException

from services import rate_limit


class AiRateLimitTests(unittest.TestCase):
    def setUp(self):
        self.original_fail_open = rate_limit.PUBLIC_RATE_LIMIT_DB_FAIL_OPEN
        rate_limit.PUBLIC_RATE_LIMIT_DB_FAIL_OPEN = True
        rate_limit.AI_RATE_LIMITS.clear()

    def tearDown(self):
        rate_limit.PUBLIC_RATE_LIMIT_DB_FAIL_OPEN = self.original_fail_open
        rate_limit.AI_RATE_LIMITS.clear()

    def test_user_is_allowed_n_requests_within_window(self):
        with patch.object(rate_limit, "get_connection", side_effect=RuntimeError("db unavailable")):
            for index in range(10):
                # Patch time.time so fallback sliding-window tests stay deterministic.
                with patch.object(rate_limit.time, "time", return_value=1000 + index):
                    rate_limit.rate_limit_ai_request(request=None, user_id=42)

        self.assertEqual(len(rate_limit.AI_RATE_LIMITS["ai:user:42"]), 10)

    def test_n_plus_one_request_returns_429(self):
        with patch.object(rate_limit, "get_connection", side_effect=RuntimeError("db unavailable")):
            for index in range(10):
                with patch.object(rate_limit.time, "time", return_value=1000 + index):
                    rate_limit.rate_limit_ai_request(request=None, user_id=42)

            with patch.object(rate_limit.time, "time", return_value=1010):
                with self.assertRaises(HTTPException) as exc:
                    rate_limit.rate_limit_ai_request(request=None, user_id=42)

        self.assertEqual(exc.exception.status_code, 429)
        self.assertEqual(exc.exception.headers["Retry-After"], "51")

    def test_counter_resets_after_window_expires(self):
        with patch.object(rate_limit, "get_connection", side_effect=RuntimeError("db unavailable")):
            for index in range(10):
                with patch.object(rate_limit.time, "time", return_value=1000 + index):
                    rate_limit._check_sliding_windows("unit", "user:42", ((10, 60),))

            with patch.object(rate_limit.time, "time", return_value=1070):
                rate_limit._check_sliding_windows("unit", "user:42", ((10, 60),))

        self.assertEqual(len(rate_limit.AI_RATE_LIMITS["unit:user:42"]), 1)


if __name__ == "__main__":
    unittest.main()
