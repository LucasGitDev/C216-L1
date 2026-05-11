# Last Test Report

- Generated at (UTC): `2026-05-11T16:19:48+00:00`
- Command: `/Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/.venv/bin/python3 -m pytest -v --junitxml /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/reports/last-test-results.xml`
- Exit code: `0`
- Result: `passed`

## Summary

| Metric | Value |
| --- | ---: |
| Test suites | 1 |
| Tests collected | 21 |
| Passed | 21 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration (s) | 1.180 |

## Test Cases

- `tests.test_app::test_create_application` [passed] (0.079s)
- `tests.test_health::test_healthcheck_returns_ok` [passed] (0.040s)
- `tests.test_health::test_process_time_middleware_adds_header` [passed] (0.033s)
- `tests.test_health::test_database_ping_returns_latency` [passed] (0.038s)
- `tests.test_openapi::test_openapi_schema_exposes_tag_metadata` [passed] (0.044s)
- `tests.test_openapi::test_openapi_student_endpoint_documents_requests_and_errors` [passed] (0.044s)
- `tests.test_openapi::test_openapi_components_include_examples_for_student_schemas` [passed] (0.040s)
- `tests.test_students::test_create_students_generates_sequential_ids_per_course` [passed] (0.071s)
- `tests.test_students::test_list_students_returns_all_seeded_students` [passed] (0.076s)
- `tests.test_students::test_get_student_returns_specific_student_by_id` [passed] (0.073s)
- `tests.test_students::test_patch_student_updates_partial_data` [passed] (0.076s)
- `tests.test_students::test_patch_student_changes_course_and_generates_new_id` [passed] (0.071s)
- `tests.test_students::test_patch_student_rejects_course_change_without_matching_email` [passed] (0.069s)
- `tests.test_students::test_delete_student_does_not_reuse_id` [passed] (0.072s)
- `tests.test_students::test_delete_all_students_resets_list_without_reusing_sequence` [passed] (0.074s)
- `tests.test_students::test_create_student_rejects_duplicate_email` [passed] (0.049s)
- `tests.test_students::test_create_student_accepts_geb_and_gep_emails` [passed] (0.048s)
- `tests.test_students::test_create_student_rejects_non_inatel_email_format` [passed] (0.037s)
- `tests.test_students::test_create_student_rejects_email_with_course_different_from_payload` [passed] (0.037s)
- `tests.test_students::test_operations_fail_for_missing_student_id` [passed] (0.044s)
- `tests.test_students::test_persistence_survives_new_connection` [passed] (0.047s)

## Console Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students
configfile: pyproject.toml
testpaths: tests
plugins: asyncio-0.26.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=session, asyncio_default_test_loop_scope=session
collected 21 items

tests/test_app.py .                                                      [  4%]
tests/test_health.py ...                                                 [ 19%]
tests/test_openapi.py ...                                                [ 33%]
tests/test_students.py ..............                                    [100%]

- generated xml file: /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/reports/last-test-results.xml -
============================== 21 passed in 1.18s ==============================
```
