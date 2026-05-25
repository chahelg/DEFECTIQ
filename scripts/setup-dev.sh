"""
Development setup script
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_backend():
    """Setup backend environment"""
    print("=" * 60)
    print("Setting up Backend")
    print("=" * 60)
    
    backend_dir = Path("backend")
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", backend_dir / "venv"], check=True)
    
    # Install dependencies
    print("Installing backend dependencies...")
    venv_python = backend_dir / "venv" / "bin" / "python"
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
    
    # Create directories
    dirs = [
        backend_dir / "uploads",
        backend_dir / "logs",
        backend_dir / "models",
        backend_dir / "embeddings",
        backend_dir / "vectordb",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {d}")
    
    # Copy .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        subprocess.run(["cp", str(backend_dir / ".env.example"), str(env_file)])
        print(f"Created .env file at {env_file}")
    
    print("Backend setup complete!\n")


def setup_frontend():
    """Setup frontend environment"""
    print("=" * 60)
    print("Setting up Frontend")
    print("=" * 60)
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing frontend dependencies...")
    os.chdir(str(frontend_dir))
    subprocess.run(["npm", "install"], check=True)
    os.chdir("..")
    
    # Copy .env file
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        subprocess.run(["cp", str(frontend_dir / ".env.example"), str(env_file)])
        print(f"Created .env file at {env_file}")
    
    print("Frontend setup complete!\n")


def setup_database():
    """Setup database"""
    print("=" * 60)
    print("Setting up Database")
    print("=" * 60)
    
    print("Database setup: Use Docker Compose to start PostgreSQL")
    print("Run: docker-compose -f docker/docker-compose.yml up -d postgres")
    print()


def main():
    """Main setup function"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DefectIQ AI - Development Environment Setup".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        setup_backend()
        setup_frontend()
        setup_database()
        
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update .env files with your configuration")
        print("2. Start Docker services: docker-compose -f docker/docker-compose.yml up")
        print("3. Backend: Run 'uvicorn app.main:app --reload' in backend directory")
        print("4. Frontend: Run 'npm run dev' in frontend directory")
        print("5. Access application at http://localhost:5173")
        print()
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

