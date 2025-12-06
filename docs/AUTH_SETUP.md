# Authentication Setup Guide

The Universal Testbook Generator uses email-based authentication to restrict access to authorized users.

## Streamlit Cloud Setup

1. Go to your app settings on Streamlit Cloud
2. Navigate to **Secrets** section
3. Add the following configuration:

```toml
# OpenAI API key
OPENAI_API_KEY = "sk-..."

# Allowed emails
allowed_emails = [
    "nicola.facchetti@si2001.it",
    "giuseppe.ferrauto@si2001.it",
    "andrea.rota@si2001.it",
    "andrea.ravasio@si2001.it"
]
```

4. Click **Save**
5. The app will restart automatically

## Local Development Setup

### Option 1: Using Streamlit Secrets (Recommended)

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your OpenAI API key
3. Update the `allowed_emails` list if needed
4. Run: `cd src && streamlit run app.py`

### Option 2: Using Environment Variables

1. Copy `.env.example` to `.env`
2. Fill in your OpenAI API key
3. Add allowed emails (comma-separated):
   ```
   ALLOWED_EMAILS=email1@example.com,email2@example.com
   ```
4. Run: `cd src && streamlit run app.py`

## How It Works

1. Users are prompted to enter their email address
2. Email is checked against the allowed list (case-insensitive)
3. If authorized, user gains access to the app
4. Session state persists until user clicks "Sign Out"

## Adding/Removing Users

### On Streamlit Cloud:
1. Go to app **Settings** → **Secrets**
2. Update the `allowed_emails` array
3. Click **Save**
4. Changes take effect immediately

### For Local Development:
1. Edit `.streamlit/secrets.toml` or `.env`
2. Update the email list
3. Restart the app

## Security Notes

- This is a **simple email whitelist**, not password-based authentication
- Suitable for trusted internal users (SI2001 team)
- Not suitable for public-facing apps or untrusted users
- Email addresses are stored in session state, not logged
- For production apps with untrusted users, consider OAuth2 or proper authentication
