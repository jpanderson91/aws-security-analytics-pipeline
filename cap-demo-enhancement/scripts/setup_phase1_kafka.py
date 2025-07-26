#!/usr/bin/env python3
"""
CAP Demo - Phase 1 Kafka Setup (Alias)
This is an alias for setup_phase1_msk.py for validation script compatibility
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the actual Phase 1 MSK setup script"""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        msk_script = script_dir / 'setup_phase1_msk.py'
        
        # Run the actual MSK setup script
        result = subprocess.run([sys.executable, str(msk_script)], 
                              capture_output=False, text=True)
        return result.returncode
    except Exception as e:
        print(f"Error running Phase 1 setup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
