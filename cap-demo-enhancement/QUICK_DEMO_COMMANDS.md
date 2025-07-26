# 🎬 Quick Demo Commands

## For Architecture & Code Demo (15 minutes)

### 1. Show Project Structure
```powershell
# Navigate to project
cd C:\Users\jpand\sec-analytics-pipeline\cap-data-ingestion-demo\consolidated

# Show structure
tree /F
```

### 2. Run Demo Validator
```powershell
# Run demo readiness check
python demo_readiness_validator.py
```

### 3. Show Documentation
```powershell
# Open key documentation files
code README.md
code docs/ARCHITECTURE.md
code docs/DEPLOYMENT_GUIDE.md
```

### 4. Show Infrastructure Code
```powershell
# Show Terraform infrastructure
code terraform/main.tf
code terraform/dashboards.tf
```

### 5. Show Automation Scripts
```powershell
# Show deployment automation
code scripts/setup_phase1_msk.py
code scripts/setup_phase2_ecs.py
code scripts/setup_phase3_analytics.py
```

## For Full Deployment Demo (30+ minutes)

### Prerequisites
```powershell
# Configure AWS credentials first
aws configure
```

### Deploy Phase 1
```powershell
cd scripts
$env:PYTHONIOENCODING="utf-8"
python setup_phase1_msk.py
```

### Deploy Phase 2
```powershell
python setup_phase2_ecs.py
```

### Deploy Phase 3
```powershell
python setup_phase3_analytics.py
```

## 🎯 Demo Key Points to Mention

1. **Enterprise Architecture**: "Real-time security analytics with AWS native services"
2. **DevOps Excellence**: "Complete Infrastructure as Code with automated deployment"
3. **Scalability**: "Container-based processing with auto-scaling capabilities"  
4. **Cost Optimization**: "Serverless components and intelligent data tiering"
5. **Professional Organization**: "Comprehensive documentation and validation automation"

## 📊 Success Metrics to Highlight

- ✅ Multi-phase deployment strategy
- ✅ Professional documentation suite
- ✅ Automated validation and testing
- ✅ Enterprise security patterns
- ✅ Cost-optimized architecture
- ✅ Real-time processing capabilities
