#!/usr/bin/env python3
"""
Interactive Installation Script for Medical Report Analysis API
Automatically detects GPU and installs appropriate dependencies
"""

import subprocess
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def check_gpu() -> bool:
    """Check if NVIDIA GPU is available."""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False


def get_cuda_version() -> str:
    """Try to detect CUDA version."""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            # Try to parse CUDA version from output
            output = result.stdout
            if "CUDA Version: 12" in output:
                return "cu121"
            elif "CUDA Version: 11" in output:
                return "cu118"
    except:
        pass
    return "cu121"  # Default to latest


def install_dependencies(gpu_support: bool = False) -> bool:
    """Install required dependencies."""
    try:
        if gpu_support:
            cuda_version = get_cuda_version()
            print(f"📦 Installing llama-cpp-python with CUDA support ({cuda_version})...")
            
            # Install llama-cpp-python with GPU support
            cmd = [
                sys.executable, "-m", "pip", "install",
                "llama-cpp-python",
                "--extra-index-url",
                f"https://abetlen.github.io/llama-cpp-python/whl/{cuda_version}"
            ]
            subprocess.run(cmd, check=True)
        
        print("📦 Installing remaining dependencies...")
        
        # Install minimal requirements
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", "requirements-minimal.txt"
        ]
        subprocess.run(cmd, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def main():
    """Main installation flow."""
    print_header("🏥 Medical Report Analysis API - Installation")
    
    print("This script will install all required dependencies.\n")
    
    # Check for GPU
    has_gpu = check_gpu()
    
    if has_gpu:
        print("✅ NVIDIA GPU detected!")
        print("   Your system supports GPU acceleration.\n")
        
        response = input("Install with GPU support? (Y/n): ").strip().lower()
        use_gpu = response != 'n'
    else:
        print("ℹ️  No NVIDIA GPU detected.")
        print("   Installation will proceed with CPU-only support.\n")
        use_gpu = False
    
    # Confirm installation
    if use_gpu:
        print("\n📋 Installation Plan:")
        print("   ✅ llama-cpp-python (with CUDA support)")
        print("   ✅ FastAPI and core dependencies")
        print("   ✅ Document processing libraries")
        print("   ✅ Testing tools")
        print("\n   🚀 Performance: GPU-accelerated (Fast)")
    else:
        print("\n📋 Installation Plan:")
        print("   ✅ llama-cpp-python (CPU only)")
        print("   ✅ FastAPI and core dependencies")
        print("   ✅ Document processing libraries")
        print("   ✅ Testing tools")
        print("\n   💻 Performance: CPU-only (Medium)")
    
    print("\n" + "-" * 80)
    response = input("\nProceed with installation? (Y/n): ").strip().lower()
    
    if response == 'n':
        print("\n❌ Installation cancelled.")
        return
    
    # Install dependencies
    print_header("Installing Dependencies")
    
    success = install_dependencies(gpu_support=use_gpu)
    
    if success:
        print_header("✅ Installation Complete!")
        
        print("🎉 All dependencies installed successfully!\n")
        
        print("📋 Next Steps:")
        print("   1. Run the API: python run.py")
        print("   2. Test the system: python test_sample.py")
        print("   3. Visit API docs: http://localhost:8000/docs")
        
        if use_gpu:
            print("\n🚀 GPU acceleration is enabled!")
            print("   The system will automatically use your GPU for inference.")
        else:
            print("\n💻 Running in CPU mode.")
            print("   For GPU support, install CUDA and run this script again.")
        
        print("\n" + "=" * 80)
    else:
        print_header("❌ Installation Failed")
        print("Please check the error messages above and try again.")
        print("\nManual installation:")
        print("   pip install -r requirements-minimal.txt")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

