# Security Best Practices (Internal)
- Never store raw PII in logs or search indices.
- Tokenize account identifiers; redact emails/SSNs/phone numbers from outputs.
- Use correlation IDs and immutable audit logs for all customer-impacting actions.
