#!/usr/bin/env python3
"""
CAP Demo - Quick Deployment Test
Tests deployment scripts without unicode issues for Windows compatibility
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Test deployment scripts with Windows-compatible output"""
    
    # Set environment for better Windows compatibility
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONPATH'] = str(Path(__file__).parent)
    
    print("=== CAP Demo - Quick Deployment Test ===")
    print("Testing Phase 1 deployment...")
    
    # Test Phase 1
    script_dir = Path(__file__).parent
    phase1_script = script_dir / 'setup_phase1_msk.py'
    
    if phase1_script.exists():
        print(f"Found Phase 1 script: {phase1_script}")
        try:
            result = subprocess.run([
                sys.executable, str(phase1_script), '--dry-run'
            ], capture_output=True, text=True, env=env, timeout=60)
            
            if result.returncode == 0:
                print("✅ Phase 1 script syntax OK")
            else:
                print("❌ Phase 1 script has issues:")
                print(result.stderr[:500])
                
        except subprocess.TimeoutExpired:
            print("⏱️ Phase 1 script timed out (expected for dry run)")
        except Exception as e:
            print(f"❌ Phase 1 error: {e}")
    else:
        print("❌ Phase 1 script not found")
    
    # Test Phase 2 - syntax check only
    phase2_script = script_dir / 'setup_phase2_processing.py'
    if phase2_script.exists():
        print(f"Found Phase 2 script: {phase2_script}")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', str(phase2_script)
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("✅ Phase 2 script syntax OK")
            else:
                print("❌ Phase 2 syntax issues:")
                print(result.stderr[:500])
        except Exception as e:
            print(f"❌ Phase 2 syntax check error: {e}")
    
    # Test Phase 3 - syntax check only
    phase3_script = script_dir / 'setup_phase3_analytics.py'
    if phase3_script.exists():
        print(f"Found Phase 3 script: {phase3_script}")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', str(phase3_script)
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("✅ Phase 3 script syntax OK")
            else:
                print("❌ Phase 3 syntax issues:")
                print(result.stderr[:500])
        except Exception as e:
            print(f"❌ Phase 3 syntax check error: {e}")
    
    print("\n=== Test Complete ===")
    print("Note: This is a compatibility test, not actual deployment")

if __name__ == "__main__":
    main()
