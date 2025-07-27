# AWS Session Management Scripts

This directory contains scripts for managing and validating AWS sessions.

## Scripts

- `aws-session-check.ps1` - Primary AWS session status checker
- `aws-sso-login.ps1` - AWS SSO login helper
- `powershell-profile-extension.ps1` - PowerShell profile enhancements
- `aws-config-template.txt` - Template for AWS configuration

## Usage

Run session check:
```powershell
.\aws-session-check.ps1 -Detailed
```

For quiet operation:
```powershell
.\aws-session-check.ps1 -Quiet
```

All scripts are Windows PowerShell compatible and sanitized for public use.
