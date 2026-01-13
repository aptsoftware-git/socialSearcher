# Enable HTTPS with Self-Signed Certificate

This guide will help you set up HTTPS for your backend server using a self-signed certificate.

## Quick Start

### Step 1: Generate SSL Certificate

Run the PowerShell script to generate a self-signed certificate:

```powershell
cd C:\Anu\code\socialSearcher\backend
.\generate_ssl_cert.ps1
```

This will:
- Create `ssl/cert.pem` (certificate)
- Create `ssl/key.pem` (private key)
- Create `ssl/cert.pfx` (Windows-compatible format)

### Step 2: Enable HTTPS in Configuration

Update your `.env` file:

```env
SSL_ENABLED=true
SSL_CERT_PATH=./ssl/cert.pem
SSL_KEY_PATH=./ssl/key.pem
```

Also update CORS to accept HTTPS connections:

```env
CORS_ORIGINS=https://localhost:5173,https://127.0.0.1:5173,https://182.73.137.36:5173
```

### Step 3: Run the Server with HTTPS

```powershell
python run_https.py
```

Your server will now be available at: `https://182.73.137.36:8000`

## Trust the Certificate (Important!)

Browsers will show a security warning because the certificate is self-signed. To trust it:

### On Windows:

1. Double-click `ssl/cert.pfx`
2. Select "Current User" → Next
3. Keep the file path → Next
4. Enter password: `password` → Next
5. Select "Place all certificates in the following store"
6. Click "Browse" → Select "Trusted Root Certification Authorities"
7. Click "Next" → "Finish"

### In Chrome/Edge:

1. Visit `https://182.73.137.36:8000` or `https://localhost:8000`
2. Click "Advanced"
3. Click "Proceed to localhost (unsafe)" or "Continue to site"

Alternatively, import the certificate:
- Chrome: Settings → Privacy and security → Security → Manage certificates → Trusted Root Certification Authorities → Import
- Edge: Same as Chrome

### In Firefox:

1. Visit `https://182.73.137.36:8000`
2. Click "Advanced"
3. Click "Accept the Risk and Continue"

## Update Frontend Configuration

Update `frontend/.env`:

```env
VITE_API_BASE_URL=https://182.73.137.36:8000
```

Then restart your frontend:

```powershell
cd C:\Anu\code\socialSearcher\frontend
npm run dev
```

## Testing

1. Visit `https://182.73.137.36:8000/docs` to verify the backend is running with HTTPS
2. Check that your frontend can communicate with the backend
3. Verify no CORS errors in the browser console

## Troubleshooting

### Certificate Error in Browser

- Make sure you've imported the certificate to "Trusted Root Certification Authorities"
- Restart your browser after importing

### CORS Errors

- Ensure CORS_ORIGINS includes HTTPS URLs
- Verify frontend is using HTTPS URL in VITE_API_BASE_URL
- Restart backend after changing .env

### Mixed Content Errors

- If frontend is HTTP and backend is HTTPS, browsers may block requests
- Either use HTTPS for both, or HTTP for both

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
Stop-Process -Id PID -Force
```

## Production Considerations

For production, consider:

1. **Get a real SSL certificate** from Let's Encrypt or a certificate authority
2. **Use a reverse proxy** like Nginx or Apache with proper SSL configuration
3. **Enable HTTP to HTTPS redirect**
4. **Set up proper firewall rules** for HTTPS (port 443)
5. **Use environment-specific .env files** (.env.production)

## Reverting to HTTP

To disable HTTPS:

```env
SSL_ENABLED=false
```

Then run the server normally:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
