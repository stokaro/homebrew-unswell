"""Reject unrelated changes and foreign PRs before opening the update for review."""

import runpy
import unittest
from pathlib import Path

PUBLISHER = runpy.run_path(str(Path(__file__).parents[1] / "scripts/prepare-update.py"))


class CandidateValidation(unittest.TestCase):
    def test_only_verified_formula_is_eligible(self):
        validate = PUBLISHER["validate_candidate"]
        validate(["Formula/unswell.rb"], "verified", "verified")
        for changed, actual in (([], "verified"), (["README.md"], "verified"),
                                (["Formula/unswell.rb", ".github/workflows/ci.yml"], "verified"),
                                (["Formula/unswell.rb"], "different")):
            with self.subTest(changed=changed, actual=actual), self.assertRaises(ValueError):
                validate(changed, "verified", actual)

    def test_pull_must_belong_to_this_app_and_repository(self):
        pull = {"baseRefName": "main", "headRefName": "release/unswell-v0.1.0-alpha.1",
                "author": {"login": "app/ptah-publish", "is_bot": True}, "isCrossRepository": False}
        validate = PUBLISHER["validate_pull"]
        validate(pull, pull["headRefName"], "app/ptah-publish")
        for key, value in (("baseRefName", "other"), ("headRefName", "other"),
                           ("author", {"login": "someone"}), ("isCrossRepository", True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(pull | {key: value}, pull["headRefName"], "app/ptah-publish")


if __name__ == "__main__":
    unittest.main()
