#!/usr/bin/env python3
"""Script to check if all required packages are installed."""

import sys
import importlib

packages_to_check = [
    'fastapi',
    'uvicorn', 
    'sqlalchemy',
    'psycopg2',
    'asyncpg',
    'multipart',
    'jose',
    'passlib',
    'pydantic',
    'pydantic_settings',
    'chromadb',
    'openai',
    'google.generativeai',
    'langchain',
    'langchain_text_splitters', 
    'dotenv',
    'supabase',
    'postgrest',
    'httpx',
    'fitz'  # PyMuPDF imports as fitz
]

missing_packages = []
installed_packages = []

for package in packages_to_check:
    try:
        # Handle special import names
        import_name = package
        if package == 'google.generativeai':
            import_name = 'google.generativeai'
        elif package == 'multipart':
            import_name = 'multipart'
        elif package == 'jose':
            import_name = 'jose'
        elif package == 'dotenv':
            import_name = 'dotenv'
            
        importlib.import_module(import_name)
        installed_packages.append(package)
        print(f"✓ {package} - installed")
    except ImportError as e:
        missing_packages.append(package)
        print(f"✗ {package} - missing ({e})")

print(f"\nSummary:")
print(f"Installed: {len(installed_packages)}")
print(f"Missing: {len(missing_packages)}")

if missing_packages:
    print(f"\nMissing packages: {missing_packages}")
else:
    print("\n🎉 All required packages are installed!")