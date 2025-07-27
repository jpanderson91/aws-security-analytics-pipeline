# Project Constraint Enforcement Template

## Quick Reminder Template for AI Interactions

Copy and paste this at the beginning of new conversations or when you notice constraints being forgotten:

---

**PROJECT CONTEXT REMINDER:**
- **Environment**: Windows PowerShell (NEVER bash)
- **Project**: AWS Security Analytics Pipeline portfolio demonstration
- **Goal**: [Insert specific current objective - NEVER suggest alternatives]
- **Protected Code**: cap-demo-enhancement/ directory is validated and working
- **Cost Target**: $15/month basic, $100-200/month enterprise
- **Shell Commands**: PowerShell syntax only (terraform, aws cli, powershell file operations)

**NON-NEGOTIABLE RULES:**
1. Complete original objective (no shortcuts or alternatives)
2. Use PowerShell commands in Windows environment
3. Preserve existing validated functionality
4. Maintain cost optimization focus
5. Enhance portfolio demonstration value
6. **NEVER commit sensitive AWS information (account IDs, SSO URLs, credentials)**

**CURRENT OBJECTIVE**: [Clearly state what you want to accomplish]

**SECURITY REMINDER**: Replace placeholder values (YOUR_AWS_ACCOUNT_ID, YOUR_SSO_DOMAIN) with actual values locally, but never commit real values to public repositories.

---

## Common Constraint Violations to Watch For

### ❌ Shell Environment Violations
```bash
# DON'T - Bash commands
mv file.txt backup/
ls -la
rm -rf directory/
```

```powershell
# DO - PowerShell commands
move file.txt backup\
get-childitem
remove-item directory\ -recurse
```

### ❌ Goal Deviation
- "Let's take a simpler approach..."
- "To save time, we could..."
- "An alternative would be..."
- "Instead of your original goal..."

### ✅ Goal Adherence
- "To accomplish your specific objective..."
- "Following your original requirements..."
- "Building on your existing approach..."
- "Maintaining your project goals..."

### ❌ Code Structure Violations
- Modifying cap-demo-enhancement/ without permission
- Suggesting non-AWS alternatives
- Ignoring cost implications
- Breaking Terraform configurations

### ✅ Code Structure Respect
- Using archive/ for development artifacts
- Enhancing README.md for portfolio value
- Adding documentation in docs/
- Preserving working Terraform configs

## Effective Prompting Strategies

### 1. Start with Context Anchor
```
"Working on AWS Security Analytics Pipeline in Windows PowerShell environment.
Current objective: [specific goal]. Please maintain project constraints."
```

### 2. Reference Instructions File
```
"Please review .github/copilot-instructions.md for project constraints before proceeding."
```

### 3. Explicit Environment Reminder
```
"Environment: Windows PowerShell. Use PowerShell syntax for all commands."
```

### 4. Goal Reinforcement
```
"Original objective is non-negotiable. Please complete [specific goal] without suggesting alternatives."
```

### 5. Code Protection
```
"Preserve all existing functionality in cap-demo-enhancement/. This is validated working code."
```

## Quick Command Reference

### PowerShell File Operations
```powershell
# Copy files
copy-item source.txt destination\

# Move files
move source.txt destination\

# Create directory
new-item -itemtype directory -path "new-folder"

# List contents
get-childitem
get-childitem -path "specific-folder"

# Remove items
remove-item filename.txt
remove-item foldername\ -recurse
```

### AWS CLI in PowerShell
```powershell
# List functions
aws lambda list-functions

# Get caller identity
aws sts get-caller-identity

# Kinesis streams
aws kinesis list-streams
```

### Terraform in PowerShell
```powershell
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply -auto-approve

# Destroy
terraform destroy -auto-approve
```

## Escalation Strategies

### When AI Forgets Constraints
1. **Immediate Correction**: "Stop. Use PowerShell syntax, not bash."
2. **Context Reinforcement**: Reference .github/copilot-instructions.md
3. **Goal Restatement**: "Original objective remains: [specific goal]"
4. **Environment Reminder**: "Working in Windows PowerShell environment"

### When AI Suggests Alternatives
1. **Firm Redirect**: "No alternatives. Complete original objective: [goal]"
2. **Constraint Reference**: "Project constraints require original approach"
3. **Value Emphasis**: "Original goal has specific portfolio demonstration value"

### When AI Wants to Modify Protected Code
1. **Hard Stop**: "cap-demo-enhancement/ is protected validated code"
2. **Alternative Location**: "Make changes in [appropriate directory] instead"
3. **Preservation Focus**: "Maintain existing functionality"
