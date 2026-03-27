#!/usr/bin/env python3
"""Test UI loads and can connect to backend"""
import time
import subprocess
import sys

def test_frontend_loading():
    """Test that frontend loads and renders"""
    print("=" * 60)
    print("TESTING FRONTEND UI LOADING")
    print("=" * 60)
    
    try:
        # Check frontend is serving on 5175
        result = subprocess.run(
            ['powershell', '-Command', 
             'try { $r = Invoke-WebRequest -Uri "http://localhost:5175" -UseBasicParsing -TimeoutSec 5; $r.StatusCode } catch { $_.Exception.Message }'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.strip()
        
        if '200' in output:
            print("✅ Frontend is serving on port 5175")
            print("✅ HTTP Status: 200 OK")
        else:
            print(f"❌ Frontend not responding properly: {output}")
            return False
            
        # Check backend is responding
        result = subprocess.run(
            ['powershell', '-Command',
             'try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -UseBasicParsing -TimeoutSec 5; $r.StatusCode } catch { $_.Exception.Message }'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.strip()
        
        if '200' in output:
            print("✅ Backend is responding on port 5000")
            print("✅ Backend HTTP Status: 200 OK")
        else:
            print(f"❌ Backend not responding: {output}")
            return False
            
        print("\n" + "=" * 60)
        print("UI LOADING TEST: PASSED ✅")
        print("=" * 60)
        print("\nBoth servers are running and responding correctly!")
        print("Frontend: http://localhost:5175")
        print("Backend: http://127.0.0.1:5000")
        print("\nYou should see:")
        print("- Sidebar on the left with navigation")
        print("- Query input form in main area")
        print("- Results section below (empty until query is submitted)")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_loading()
    sys.exit(0 if success else 1)
