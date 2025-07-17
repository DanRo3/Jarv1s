#!/usr/bin/env python3
"""
Automated setup script for Jarv1s.
Handles installation, model downloads, and environment verification.
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path
from typing import List, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SetupManager:
    """Manages the Jarv1s setup process."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "models" / "tts"
        
    def log(self, message: str, color: str = Colors.BLUE) -> None:
        """Log a message with color."""
        print(f"{color}[SETUP]{Colors.END} {message}")
    
    def success(self, message: str) -> None:
        """Log a success message."""
        self.log(f"✅ {message}", Colors.GREEN)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log(f"⚠️  {message}", Colors.YELLOW)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self.log(f"❌ {message}", Colors.RED)
    
    def run_command(self, command: List[str], description: str) -> bool:
        """Run a command and return success status."""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.error(f"Failed: {description}")
            self.error(f"Error: {e.stderr}")
            return False
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        self.log("Checking Python version...")
        
        if sys.version_info < (3, 11):
            self.error(f"Python 3.11+ required, found {sys.version}")
            return False
        
        self.success(f"Python {sys.version.split()[0]} is compatible")
        return True
    
    def check_system_dependencies(self) -> bool:
        """Check if system dependencies are installed."""
        self.log("Checking system dependencies...")
        
        dependencies = [
            ("ffmpeg", "FFmpeg for audio processing"),
            ("git", "Git for version control")
        ]
        
        all_found = True
        for cmd, description in dependencies:
            try:
                subprocess.run([cmd, "--version"], 
                             check=True, 
                             capture_output=True)
                self.success(f"{description} found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.error(f"{description} not found")
                all_found = False
        
        if not all_found:
            self.warning("Install missing dependencies:")
            self.warning("Ubuntu/Debian: sudo apt install ffmpeg git")
            self.warning("macOS: brew install ffmpeg git")
            self.warning("Windows: choco install ffmpeg git")
        
        return all_found
    
    def setup_virtual_environment(self) -> bool:
        """Create and setup virtual environment."""
        venv_path = self.project_root / ".venv"
        
        if venv_path.exists():
            self.success("Virtual environment already exists")
            return True
        
        self.log("Creating virtual environment...")
        if not self.run_command([
            sys.executable, "-m", "venv", str(venv_path)
        ], "Create virtual environment"):
            return False
        
        self.success("Virtual environment created")
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.log("Installing Python dependencies...")
        
        venv_python = self.project_root / ".venv" / "bin" / "python"
        if not venv_python.exists():
            # Windows path
            venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            self.error("Virtual environment Python not found")
            return False
        
        # Install in development mode
        if not self.run_command([
            str(venv_python), "-m", "pip", "install", "-e", "."
        ], "Install Jarv1s package"):
            return False
        
        self.success("Python dependencies installed")
        return True
    
    def download_tts_models(self) -> bool:
        """Download TTS models."""
        self.log("Setting up TTS models...")
        
        # Create models directory
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        models = [
            {
                "name": "es_ES-sharvard-medium.onnx",
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
            },
            {
                "name": "es_ES-sharvard-medium.onnx.json", 
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
            }
        ]
        
        for model in models:
            model_path = self.models_dir / model["name"]
            
            if model_path.exists():
                self.success(f"Model {model['name']} already exists")
                continue
            
            self.log(f"Downloading {model['name']}...")
            try:
                urllib.request.urlretrieve(model["url"], model_path)
                self.success(f"Downloaded {model['name']}")
            except Exception as e:
                self.error(f"Failed to download {model['name']}: {e}")
                return False
        
        return True
    
    def setup_environment_file(self) -> bool:
        """Setup .env file from template."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            self.success(".env file already exists")
            return True
        
        if not env_example.exists():
            self.error(".env.example not found")
            return False
        
        self.log("Creating .env file from template...")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            self.success(".env file created")
            self.warning("Please review and update .env file with your settings")
            return True
        except Exception as e:
            self.error(f"Failed to create .env file: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic tests to verify installation."""
        self.log("Running verification tests...")
        
        venv_python = self.project_root / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        
        test_script = """
import sys
sys.path.insert(0, 'src')

try:
    from src.config.settings import get_settings
    from src.utils.logger import get_main_logger
    
    settings = get_settings()
    logger = get_main_logger()
    
    print("✅ Configuration system working")
    print("✅ Logging system working")
    print("✅ Basic imports successful")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
"""
        
        try:
            result = subprocess.run([
                str(venv_python), "-c", test_script
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.success("Verification tests passed")
                return True
            else:
                self.error(f"Tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.error(f"Failed to run tests: {e}")
            return False
    
    def print_next_steps(self) -> None:
        """Print next steps for the user."""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Setup completed successfully!{Colors.END}\n")
        
        print(f"{Colors.BOLD}Next steps:{Colors.END}")
        print("1. Activate the virtual environment:")
        print(f"   {Colors.BLUE}source .venv/bin/activate{Colors.END}  # Linux/macOS")
        print(f"   {Colors.BLUE}.venv\\Scripts\\activate{Colors.END}     # Windows")
        
        print("\n2. Start LM Studio and load a model")
        
        print("\n3. Start the Jarv1s backend:")
        print(f"   {Colors.BLUE}python -m src.main{Colors.END}")
        
        print("\n4. Start the frontend (in another terminal):")
        print(f"   {Colors.BLUE}cd frontend && npm install && npm run dev{Colors.END}")
        
        print(f"\n5. Open your browser to {Colors.BLUE}http://localhost:5173{Colors.END}")
        
        print(f"\n{Colors.YELLOW}For Docker/Podman setup:{Colors.END}")
        print(f"   {Colors.BLUE}./scripts/podman-dev.sh{Colors.END}")
    
    def run_setup(self) -> bool:
        """Run the complete setup process."""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 Jarv1s Setup Script{Colors.END}\n")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Setting up virtual environment", self.setup_virtual_environment),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Downloading TTS models", self.download_tts_models),
            ("Setting up environment file", self.setup_environment_file),
            ("Running verification tests", self.run_tests),
        ]
        
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not step_func():
                self.error(f"Setup failed at: {step_name}")
                return False
            print()  # Add spacing between steps
        
        self.print_next_steps()
        return True


def main():
    """Main entry point."""
    setup = SetupManager()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        setup.warning("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        setup.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()