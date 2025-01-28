# pluton-core

# How to generate models

```
alembic revision --autogenerate -m "init"
```

> Be careful to check the version of the migration file

```
alembic upgrade head
```

## Referral

### Endpoint:

- POST /api/ref/use
- body: `{
  "access_token": "string",
  "ref_code": "string"
}`
- Successfull response: `{
              "message": "Referral code used successfully"
          }`

We can check User["used_ref_code"]!="" to verify if the account have used ref code
