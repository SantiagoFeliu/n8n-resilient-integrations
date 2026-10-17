# n8n Resilient Integrations

A small, public-by-design portfolio of synthetic n8n workflows demonstrating webhook contracts, validation, structured responses, bounded retries, idempotency, and recovery routing.

## Included examples

1. **Validate inbound order webhook** — validates a synthetic order payload and returns explicit `202` or `400` JSON responses.
2. **Process delivery with bounded retry and recovery** — models idempotency, a maximum of three attempts, retryable `503` responses, and a terminal recovery response.

These examples intentionally do not call a real provider. External integrations can be substituted with a test double such as `https://example.com` or a local mock service.

## Compatibility

Validated with n8n `2.43.7` in an isolated Docker container. Node behavior can vary across n8n releases; re-run the included structural audit and the HTTP cases after import.

## Import and test

1. Import either JSON file from `workflows/` into a non-production n8n workspace.
2. Keep the workflows inactive until reviewed.
3. Use the generated test payloads below against the test webhook URL shown by n8n.

Success payload:
```json
{"orderId":"demo-1001","email":"demo@example.com","amount":42.50}
```

Invalid payload:
```json
{"orderId":"demo-1002","email":"not-an-email","amount":0}
```

Retryable delivery:
```json
{"idempotencyKey":"demo-key-001","attempt":1,"simulatedResult":"transient_failure"}
```

Terminal recovery:
```json
{"idempotencyKey":"demo-key-001","attempt":3,"simulatedResult":"transient_failure"}
```

## Architecture notes

Both workflows use a webhook trigger, explicit normalization/validation, an `If` decision, and a response node. The retry example does not silently loop: the caller receives the next attempt number and owns the retry schedule. This keeps retry policy bounded and makes duplicate-prevention responsibility explicit through the idempotency key; a production implementation must persist and atomically claim that key.

## Security and scope

- All names, IDs, payloads, and endpoints are synthetic.
- No credentials, tokens, production exports, customer data, infrastructure addresses, or operational logs are included.
- No workflow is active by default.
- This repository is a demonstration, not a production-ready integration. Review node behavior and n8n version compatibility before use.
- No claim is made about absolute security; the included audit is bounded to repository contents and structural checks.

## Repository hygiene

`tests/validate_repo.py` performs JSON parsing, connection-reference checks, inactive-state checks, and a small secret-marker scan. Run:

```bash
python3 tests/validate_repo.py
```

## License

MIT. See `LICENSE`.
