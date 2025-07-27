# Safe File Cleanup Execution Plan

## 🎯 Specific Actions Identified

### Files Ready for Safe Cleanup

#### 1. Consolidate AWS Session Scripts
**Current:** Two very similar AWS session check scripts
```
- /scripts/aws-session/aws-session-check.ps1 (with Unicode)
- /scripts/aws-session/aws-session-check-simple.ps1 (without Unicode)
```

**Action:** Keep the simple version for better Windows compatibility

#### 2. Move Orphaned Test Files
**Current:** Test files in root that should be in appropriate directories
```
- test_cap_environment.py (root) → should be in /archive/
```

**Action:** Archive the root version since active version is in cap-demo-enhancement/tests/

#### 3. Archive Legacy Setup Scripts
**Current:** Old setup scripts in root directory
```
- setup_cap_demo.ps1 (root) → already copied to /archive/
- setup_cap_demo_fixed.ps1 (root) → already copied to /archive/
```

**Action:** Remove from root since they're already in archive/

#### 4. Create Missing Directory READMEs
**Missing Documentation:**
- /scripts/aws-session/ needs README.md
- Root /scripts/ needs README.md explaining structure

## 🔧 Execution Commands

### Phase 1: Archive Orphaned Files
```powershell
# Move orphaned test file to archive (if not already there)
if (Test-Path "C:\Projects\aws-security-analytics-pipeline\test_cap_environment.py") {
    Move-Item "test_cap_environment.py" "archive\"
    Write-Host "Archived orphaned test_cap_environment.py" -ForegroundColor Green
}

# Remove setup scripts from root (already in archive)
if (Test-Path "C:\Projects\aws-security-analytics-pipeline\setup_cap_demo.ps1") {
    Remove-Item "setup_cap_demo.ps1"
    Write-Host "Removed setup_cap_demo.ps1 from root (already in archive)" -ForegroundColor Green
}

if (Test-Path "C:\Projects\aws-security-analytics-pipeline\setup_cap_demo_fixed.ps1") {
    Remove-Item "setup_cap_demo_fixed.ps1"
    Write-Host "Removed setup_cap_demo_fixed.ps1 from root (already in archive)" -ForegroundColor Green
}
```

### Phase 2: AWS Session Script Consolidation
```powershell
# Keep the simple version, remove the Unicode version for Windows compatibility
Remove-Item "scripts\aws-session\aws-session-check.ps1"
Write-Host "Removed Unicode version of aws-session-check.ps1" -ForegroundColor Green

# Rename the simple version to be the primary version
Rename-Item "scripts\aws-session\aws-session-check-simple.ps1" "aws-session-check.ps1"
Write-Host "Promoted simple version to primary aws-session-check.ps1" -ForegroundColor Green
```

### Phase 3: Add Missing Documentation
```powershell
# Create README for scripts directory
$scriptsReadmeContent = @"
# Scripts Directory

This directory contains utility scripts for the AWS Security Analytics Pipeline project.

## Directory Structure

- `/aws-session/` - AWS session management and validation scripts

## Usage

All scripts are designed for PowerShell on Windows and follow the project's coding standards.

For detailed script documentation, see individual script headers.
"@

$scriptsReadmeContent | Out-File -FilePath "scripts\README.md" -Encoding UTF8

# Create README for aws-session directory
$awsSessionReadmeContent = @"
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
"@

$awsSessionReadmeContent | Out-File -FilePath "scripts\aws-session\README.md" -Encoding UTF8

Write-Host "Created missing README files" -ForegroundColor Green
```

## ✅ Safety Checks

### Before Execution Checklist
- [ ] Git status is clean
- [ ] All important changes are committed
- [ ] No active deployments running
- [ ] Backup of current state created

### Validation Commands
```powershell
# Verify no important files will be lost
Write-Host "Files that will be removed:" -ForegroundColor Yellow
Get-ChildItem "setup_cap_demo*.ps1" | Select-Object Name, FullName
Get-ChildItem "test_cap_environment.py" | Select-Object Name, FullName

# Verify archive directory has the files
Write-Host "Files in archive:" -ForegroundColor Green
Get-ChildItem "archive\" | Select-Object Name
```

### Post-Cleanup Validation
```powershell
# Test that critical scripts still work
.\scripts\aws-session\aws-session-check.ps1 -Quiet

# Verify deployment still works
cd cap-demo-enhancement
python tests\demo_readiness_validator.py
```

## 📊 Expected Results

### Space Savings
- **Minimal** - focus is on organization, not space
- Remove ~3 duplicate/orphaned files
- Add 2 documentation files

### Organization Improvements
- ✅ Clear script directory structure
- ✅ No orphaned files in root
- ✅ Consistent AWS session management
- ✅ Better documentation coverage

### Risk Assessment
- **Risk Level:** Very Low
- **Files affected:** 5 files (3 removed, 2 added)
- **Critical path impact:** None
- **Rollback complexity:** Simple (Git revert)

## 🚀 Execution Ready

This plan is ready for execution and includes:
- ✅ Safety checks
- ✅ Detailed commands
- ✅ Validation steps
- ✅ Clear expected outcomes
- ✅ Low risk assessment

All changes maintain project functionality while improving organization and documentation.
