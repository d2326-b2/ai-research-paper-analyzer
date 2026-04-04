# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in HypoGen, please email **security@hypogen.ai** instead of using the issue tracker.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We take security very seriously and will acknowledge your report within 48 hours.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## Security Best Practices

When using HypoGen:

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique `SECRET_KEY` values
- Rotate API keys regularly
- Use `.env.example` as a template only

### Password Security
- Passwords are hashed with bcrypt (automatically)
- Minimum 6 characters recommended (enforce in production)
- Consider rate limiting login attempts

### API Keys
- Keep Gemini API keys confidential
- Use project-specific API keys where possible
- Monitor API usage for suspicious activity

### Deployment
- Always use HTTPS in production
- Set `FLASK_DEBUG = False` in production
- Use strong database credentials
- Configure CORS appropriately for your domain
- Run behind a reverse proxy (nginx, Apache)
- Keep dependencies updated

### File Uploads
- Validate file types on both client and server
- Limit file size appropriately
- Store uploaded PDFs securely
- Clean up temporary files after processing

## Dependency Security

We regularly update dependencies to patch security vulnerabilities. Always keep your installation up to date:

```bash
pip install --upgrade -r backend/requirements.txt
```

## Vulnerability Disclosure

We follow responsible disclosure and will:
- Acknowledge receipt of your report
- Work on a fix
- Issue a security update
- Give appropriate credit (if desired)

Thank you for helping keep HypoGen secure! 🔒
