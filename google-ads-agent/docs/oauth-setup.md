# OAuth setup

Fifteen minutes, once.

## 1. Google Cloud project

1. <https://console.cloud.google.com/> → create a project (or reuse one).
2. **APIs & Services → Library** → enable **Google Ads API**.
3. **APIs & Services → OAuth consent screen**:
   - User type: Internal if you have Google Workspace, otherwise External.
   - External projects start in "Testing" - add the Google account that manages
     the ads accounts under **Test users**, or the refresh token will expire
     every 7 days.
   - Scope: `https://www.googleapis.com/auth/adwords`.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type: **Desktop app**.
   - Save the client id and client secret.

## 2. Refresh token

```
cd google-ads-agent
pip install -r requirements.txt
python scripts/setup_oauth.py --client-id XXX --client-secret YYY
```

A browser opens; sign in as the user who can see the Google Ads accounts and
approve. The script prints the three lines to paste into `.env`.

On a server or in a container without a browser:

```
python scripts/setup_oauth.py --client-id XXX --client-secret YYY --console
```

## 3. Fill in .env

```
cp .env.example .env
```

```
GOOGLE_ADS_DEVELOPER_TOKEN=...        # from API Center (see developer-token-application.md)
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
GOOGLE_ADS_REFRESH_TOKEN=...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890    # the MCC, digits only
GOOGLE_ADS_DEFAULT_CUSTOMER_ID=9876543210  # the practice you work on most
GADS_MOCK=0
```

## 4. Check it

```
python -m gads.selfcheck
```

It prints the mode, the accounts the token can see, the account's name and
timezone, the practice config it found, and what the guardrails currently allow.

## When something fails

| Symptom | Cause |
|---|---|
| `invalid_client` | Client id/secret do not match the project, or the OAuth client was deleted |
| `invalid_grant` | Refresh token revoked or expired - re-run `setup_oauth.py`. External consent screens in "Testing" expire tokens after 7 days; publish the app or add the user as a test user |
| `DEVELOPER_TOKEN_NOT_APPROVED` | Test-level token against a production account |
| `USER_PERMISSION_DENIED` | The signed-in user cannot see that customer id, or `login_customer_id` is not the manager of it |
| `CUSTOMER_NOT_ENABLED` | The account is cancelled or suspended (usually billing) |

Never commit `.env`. It is already in `.gitignore`.
