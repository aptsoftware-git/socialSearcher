"""
Run the FastAPI application with HTTPS support using self-signed certificate.
"""
import uvicorn
import os
import ssl
from pathlib import Path

if __name__ == "__main__":
    # Get SSL configuration from environment or use defaults
    ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
    ssl_cert_path = os.getenv("SSL_CERT_PATH", "./ssl/cert.pem")
    ssl_key_path = os.getenv("SSL_KEY_PATH", "./ssl/key.pem")
    ssl_pfx_path = "./ssl/cert.pfx"
    ssl_pfx_password = "password"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting server on {host}:{port}")
    print(f"SSL Enabled: {ssl_enabled}")
    
    if ssl_enabled:
        cert_file = Path(ssl_cert_path)
        key_file = Path(ssl_key_path)
        pfx_file = Path(ssl_pfx_path)
        
        # Try PEM files first
        if cert_file.exists() and key_file.exists():
            print(f"Certificate: {cert_file}")
            print(f"Private Key: {key_file}")
            print(f"\nServer will be available at: https://{host}:{port}")
            print("Note: Browsers will show a security warning for self-signed certificates")
            
            uvicorn.run(
                "app.main:app",
                host=host,
                port=port,
                ssl_keyfile=str(key_file),
                ssl_certfile=str(cert_file),
                reload=True
            )
        # Fall back to PFX if PEM not available
        elif pfx_file.exists():
            print(f"Using PFX certificate: {pfx_file}")
            print(f"\nServer will be available at: https://{host}:{port}")
            print("Note: Browsers will show a security warning for self-signed certificates")
            print("\nConverting PFX to PEM for uvicorn...")
            
            # Convert PFX to PEM using OpenSSL if available
            import subprocess
            try:
                # Extract certificate
                subprocess.run([
                    "openssl", "pkcs12", "-in", str(pfx_file), 
                    "-clcerts", "-nokeys", "-out", str(cert_file),
                    "-passin", f"pass:{ssl_pfx_password}", "-passout", "pass:"
                ], check=True)
                
                # Extract private key
                subprocess.run([
                    "openssl", "pkcs12", "-in", str(pfx_file),
                    "-nocerts", "-nodes", "-out", str(key_file),
                    "-passin", f"pass:{ssl_pfx_password}", "-passout", "pass:"
                ], check=True)
                
                print("✓ PFX converted to PEM successfully")
                
                uvicorn.run(
                    "app.main:app",
                    host=host,
                    port=port,
                    ssl_keyfile=str(key_file),
                    ssl_certfile=str(cert_file),
                    reload=True
                )
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("ERROR: OpenSSL not found or conversion failed")
                print("Please install OpenSSL or manually convert PFX to PEM files")
                exit(1)
        else:
            print(f"ERROR: SSL certificate files not found")
            print(f"Looked for: {cert_file} and {key_file}")
            print(f"Or: {pfx_file}")
            print("Run 'generate_ssl_cert.ps1' to create a self-signed certificate")
            exit(1)
    else:
        print(f"\nServer will be available at: http://{host}:{port}")
        print("To enable HTTPS, set SSL_ENABLED=true in .env")
        
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True
        )
