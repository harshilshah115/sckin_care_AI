"""
Django Backend Setup Script
Run this script to initialize the Django project structure.

Usage:
    cd "d:\Harshil Projects\Sckin Care\backend"
    python setup_backend.py
"""

import os
import subprocess
import sys

def run_command(command, description):
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    print(f"✅ Success: {description}")
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       AI Skincare Assistant - Backend Setup Script           ║
╠══════════════════════════════════════════════════════════════╣
║  This script will:                                           ║
║  1. Create a virtual environment                             ║
║  2. Install Django and dependencies                          ║
║  3. Create the Django project structure                      ║
║  4. Create all necessary apps                                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Create virtual environment
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Step 2: Activate venv and install dependencies
    pip_cmd = 'venv\\Scripts\\pip' if os.name == 'nt' else 'venv/bin/pip'
    
    dependencies = [
        'django==5.0.2',
        'djangorestframework==3.14.0',
        'djangorestframework-simplejwt==5.3.1',
        'django-cors-headers==4.3.1',
        'pillow==10.2.0',
        'python-dotenv==1.0.1',
    ]
    
    print("\n📦 Installing dependencies...")
    for dep in dependencies:
        run_command(f'{pip_cmd} install {dep}', f'Installing {dep.split("==")[0]}')
    
    # Step 3: Create Django project
    django_admin = 'venv\\Scripts\\django-admin' if os.name == 'nt' else 'venv/bin/django-admin'
    
    if not os.path.exists('skincare'):
        run_command(f'{django_admin} startproject skincare .', 'Creating Django project')
    else:
        print("✅ Django project already exists")
    
    # Step 4: Create apps directory and apps
    python_cmd = 'venv\\Scripts\\python' if os.name == 'nt' else 'venv/bin/python'
    
    if not os.path.exists('apps'):
        os.makedirs('apps')
        # Create __init__.py
        with open('apps/__init__.py', 'w') as f:
            f.write('')
    
    apps = ['users', 'skincare_analysis', 'recommendations', 'products', 'history']
    
    for app in apps:
        app_path = f'apps/{app}'
        if not os.path.exists(app_path):
            os.makedirs(app_path)
            run_command(f'{python_cmd} manage.py startapp {app} {app_path}', f'Creating {app} app')
        else:
            print(f"✅ App {app} already exists")
    
    # Step 5: Create media directory
    if not os.path.exists('media/skin_scans'):
        os.makedirs('media/skin_scans')
        print("✅ Created media/skin_scans directory")
    
    # Step 6: Generate requirements.txt
    run_command(f'{pip_cmd} freeze > requirements.txt', 'Generating requirements.txt')
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ SETUP COMPLETE!                        ║
╠══════════════════════════════════════════════════════════════╣
║  Next steps:                                                 ║
║  1. Update skincare/settings.py with the provided config     ║
║  2. Create the User model in apps/users/models.py            ║
║  3. Run: python manage.py makemigrations                     ║
║  4. Run: python manage.py migrate                            ║
║  5. Run: python manage.py runserver                          ║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
