# pluton-core

## Referral
### Endpoint: 
- POST /api/ref/use
- body: ```{
  "access_token": "string",
  "ref_code": "string"
}```
- Successfull response: ```{
                "message": "Referral code used successfully"
            }```

We can check User["used_ref_code"]!="" to verify if the account have used ref code
