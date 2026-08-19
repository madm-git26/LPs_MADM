#!/usr/bin/env python3
"""One-time: turn an OAuth client into a refresh token.

Before running this you need an OAuth client of type **Desktop app** from
Google Cloud Console (APIs & Services -> Credentials), with the Google Ads API
enabled on the project.  See docs/oauth-setup.md.

    python scripts/setup_oauth.py --client-id ... --client-secret ...

It opens a browser (or prints a URL), you log in as a user who can see the
Google Ads accounts, and it prints the refresh token to paste into .env.
"""

from __future__ import annotations

import argparse
import sys

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--port", type=int, default=8080,
                        help="Local port for the OAuth redirect (default 8080).")
    parser.add_argument("--console", action="store_true",
                        help="Print a URL instead of opening a browser - use this on a "
                             "server or in a container.")
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Install the dependencies first: pip install -r requirements.txt")
        return 1

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": args.client_id,
                "client_secret": args.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        scopes=SCOPES,
    )

    if args.console:
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print("\nOpen this URL, approve access, then paste the code back here:\n")
        print(auth_url)
        code = input("\nCode: ").strip()
        flow.fetch_token(code=code)
    else:
        # access_type=offline + prompt=consent is what actually returns a refresh
        # token; without them Google hands back an access token only.
        flow.run_local_server(port=args.port, prompt="consent", access_type="offline")

    credentials = flow.credentials
    if not credentials.refresh_token:
        print("\nGoogle did not return a refresh token. Revoke the app's access at "
              "https://myaccount.google.com/permissions and run this again.")
        return 1

    print("\nAdd these to google-ads-agent/.env:\n")
    print(f"GOOGLE_ADS_CLIENT_ID={args.client_id}")
    print(f"GOOGLE_ADS_CLIENT_SECRET={args.client_secret}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
    print("\nThen add your developer token and MCC id, and run:  python -m gads.selfcheck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
