# Last Test Report

- Generated at (UTC): `2026-04-21T19:37:09+00:00`
- Command: `/Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/.venv/bin/python3 -m pytest -v --junitxml /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/reports/last-test-results.xml`
- Exit code: `0`
- Result: `passed`

## Summary

| Metric | Value |
| --- | ---: |
| Test suites | 1 |
| Tests collected | 19 |
| Passed | 19 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration (s) | 0.633 |

## Test Cases

- `tests.test_app::test_create_application` [passed] (0.006s)
- `tests.test_health::test_healthcheck_returns_ok` [passed] (0.015s)
- `tests.test_health::test_process_time_middleware_adds_header` [passed] (0.011s)
- `tests.test_openapi::test_openapi_schema_exposes_tag_metadata` [passed] (0.055s)
- `tests.test_openapi::test_openapi_student_endpoint_documents_requests_and_errors` [passed] (0.079s)
- `tests.test_openapi::test_openapi_components_include_examples_for_student_schemas` [passed] (0.054s)
- `tests.test_students::test_create_students_generates_sequential_ids_per_course` [passed] (0.033s)
- `tests.test_students::test_list_students_returns_all_seeded_students` [passed] (0.030s)
- `tests.test_students::test_get_student_returns_specific_student_by_id` [passed] (0.032s)
- `tests.test_students::test_patch_student_updates_partial_data` [passed] (0.033s)
- `tests.test_students::test_patch_student_changes_course_and_generates_new_id` [passed] (0.032s)
- `tests.test_students::test_patch_student_rejects_course_change_without_matching_email` [passed] (0.035s)
- `tests.test_students::test_delete_student_does_not_reuse_id` [passed] (0.033s)
- `tests.test_students::test_delete_all_students_resets_list_without_reusing_sequence` [passed] (0.043s)
- `tests.test_students::test_create_student_rejects_duplicate_email` [passed] (0.019s)
- `tests.test_students::test_create_student_accepts_geb_and_gep_emails` [passed] (0.018s)
- `tests.test_students::test_create_student_rejects_non_inatel_email_format` [passed] (0.017s)
- `tests.test_students::test_create_student_rejects_email_with_course_different_from_payload` [passed] (0.015s)
- `tests.test_students::test_operations_fail_for_missing_student_id` [passed] (0.017s)

## Console Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0
collected 19 items

tests/test_app.py .                                                      [  5%]
tests/test_health.py ..                                                  [ 15%]
tests/test_openapi.py ...                                                [ 31%]
tests/test_students.py .............                                     [100%]

- generated xml file: /Users/lucas/dev/lucas/inatel/C216-L1/004-crud-students/reports/last-test-results.xml -
============================== 19 passed in 0.63s ==============================
```
