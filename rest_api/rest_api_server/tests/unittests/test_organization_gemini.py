from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestOrganizationGemini(TestApiBase):
    def setUp(self, version="v2"):
        super().setUp(version)

        self.filters = {
            "filters": {
                "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                "buckets": "bucket1,bucket2",
                "min_size": 1
            }
        }

        _, self.organization = self.client.organization_create({"name": "partner"})
        self.organization_id = self.organization["id"]
        self.code_1, self.gemini_1 = self.client.gemini_create(
            self.organization_id, self.filters
        )
        self.code_2, self.gemini_2 = self.client.gemini_create(
            self.organization_id, self.filters
        )

    def test_create_gemini(self):
        self.assertEqual(self.code_1, 201)
        self.assertEqual(self.gemini_1["organization_id"], self.organization_id)
        self.assertIn("stats", self.gemini_1)
        self.assertIn("status", self.gemini_1)
        self.assertIn("filters", self.gemini_1)

        self.assertEqual(self.code_2, 201)
        self.assertEqual(self.gemini_2["organization_id"], self.organization_id)
        self.assertIn("stats", self.gemini_2)
        self.assertIn("status", self.gemini_2)
        self.assertIn("filters", self.gemini_2)

    def test_list_geminis(self):
        code, result = self.client.gemini_list(self.organization_id)
        geminis = result["geminis"]

        self.assertEqual(code, 200)
        self.assertEqual(len(geminis), 2)
        self.assertEqual(geminis[0]["organization_id"], geminis[1]["organization_id"])
        self.assertEqual(geminis[0]["status"], "CREATED")
        self.assertEqual(geminis[1]["status"], "CREATED")

    def test_get_gemini(self):
        code, gemini = self.client.gemini_get(self.gemini_1["id"])

        self.assertEqual(code, 200)
        self.assertIn("stats", gemini)
        self.assertIn("status", gemini)
        self.assertIn("filters", gemini)

    def test_patch_gemini_status(self):
        body = {"status": "RUNNING"}
        code, gemini = self.client.gemini_update(self.gemini_1["id"], body)
        self.assertEqual(code, 200)
        self.assertEqual(gemini["status"], "RUNNING")

    def test_patch_gemini_stats(self):
        body = {
            "stats": {
                "total_objects": 123,
                "filtered_objects": 12,
                "total_size": 12345,
                "duplicates_size": 321,
                "duplicated_objects": 15,
                "monthly_savings": 321,
                "buckets": {
                    "bucket_1": {
                        "total_objects": 5,
                        "filtered_objects": 5,
                        "size": 243049,
                        "daily_cost": 1.681e-07},
                    "bucket_2": {
                        "total_objects": 4,
                        "filtered_objects": 4,
                        "size": 169291,
                        "daily_cost": 1.171e-07}
                },
                "matrix": {
                    "bucket_1": {
                        "bucket_1": {
                            "duplicated_objects": 3,
                            "duplicates_size": 142458.0,
                        },
                        "bucket_2": {
                            "duplicated_objects": 7,
                            "duplicates_size": 169291,
                        },
                    },
                    "bucket_2": {
                        "bucket_2": {"duplicated_objects": 0, "duplicates_size": 0},
                        "bucket_1": {
                            "duplicated_objects": 7,
                            "duplicates_size": 169291,
                        },
                    },
                }
            }
        }
        code, gemini = self.client.gemini_update(self.gemini_1["id"], body)

        self.assertEqual(code, 200)
        stats = gemini["stats"]
        self.assertEqual(stats["total_objects"], 123)
        self.assertEqual(stats["filtered_objects"], 12)
        self.assertEqual(stats["total_size"], 12345)
        self.assertEqual(stats["duplicates_size"], 321)
        self.assertEqual(stats["duplicated_objects"], 15)
        self.assertIn("buckets", stats)
        self.assertIn("matrix", stats)

    def test_get_not_existing_gemini(self):
        code, data = self.client.gemini_get("123")
        self.assertEqual(code, 404)
        self.assertEqual(data["error"]["error_code"], "OE0002")

    def test_delete_gemini(self):
        _, gemini = self.client.gemini_create(
            self.organization_id, self.filters
        )

        code, _ = self.client.gemini_delete(gemini["id"])
        self.assertEqual(204, code)
