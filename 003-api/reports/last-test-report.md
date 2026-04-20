# Last Test Report

- Generated at (UTC): `2026-04-20T13:15:59+00:00`
- Command: `/Users/lucas/dev/lucas/inatel/C216-L1/003-api/.venv/bin/python3 -m pytest -v --junitxml /Users/lucas/dev/lucas/inatel/C216-L1/003-api/reports/last-test-results.xml`
- Exit code: `0`
- Result: `passed`

## Summary

| Metric | Value |
| --- | ---: |
| Test suites | 1 |
| Tests collected | 18 |
| Passed | 18 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration (s) | 1.200 |

## Test Cases

- `tests.test_app::test_create_application` [passed] (0.002s)
- `tests.test_health::test_healthcheck_returns_ok` [passed] (0.004s)
- `tests.test_health::test_process_time_middleware_adds_header` [passed] (0.003s)
- `tests.test_microwaves::test_list_microwaves_returns_two_preloaded_instances` [passed] (0.003s)
- `tests.test_microwaves::test_create_microwave_returns_new_instance` [passed] (0.003s)
- `tests.test_microwaves::test_get_microwave_returns_specific_state` [passed] (0.003s)
- `tests.test_microwaves::test_start_microwave_updates_state` [passed] (0.003s)
- `tests.test_microwaves::test_start_microwave_rejects_empty_content` [passed] (0.003s)
- `tests.test_microwaves::test_start_microwave_rejects_when_running` [passed] (0.003s)
- `tests.test_microwaves::test_stop_microwave_turns_it_off` [passed] (0.003s)
- `tests.test_microwaves::test_stop_microwave_rejects_when_already_stopped` [passed] (0.002s)
- `tests.test_microwaves::test_reset_microwave_returns_default_state` [passed] (0.004s)
- `tests.test_microwaves::test_delete_created_microwave_removes_instance` [passed] (0.004s)
- `tests.test_microwaves::test_operations_fail_for_removed_id` [passed] (0.004s)
- `tests.test_microwaves::test_expired_timer_is_reflected_as_finished` [passed] (1.110s)
- `tests.test_openapi::test_openapi_schema_exposes_tag_metadata` [passed] (0.016s)
- `tests.test_openapi::test_openapi_start_endpoint_documents_requests_and_errors` [passed] (0.010s)
- `tests.test_openapi::test_openapi_components_include_examples_for_microwave_schemas` [passed] (0.009s)

## Console Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/lucas/dev/lucas/inatel/C216-L1/003-api
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0
collected 18 items

tests/test_app.py .                                                      [  5%]
tests/test_health.py ..                                                  [ 16%]
tests/test_microwaves.py ............                                    [ 83%]
tests/test_openapi.py ...                                                [100%]

- generated xml file: /Users/lucas/dev/lucas/inatel/C216-L1/003-api/reports/last-test-results.xml -
============================== 18 passed in 1.20s ==============================
```
