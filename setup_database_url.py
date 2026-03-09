#!/usr/bin/env python3
"""
Helper script to add Supabase DATABASE_URL to .env file
"""

import os

print("="*60)
print("Supabase Database URL Setup")
print("="*60)

print("\nYour Supabase connection string should look like:")
print("postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres")
print("\nMake sure to replace [YOUR-PASSWORD] with your actual database password!")
print("\n" + "="*60)

database_url = input("\nPaste your Supabase connection string here: ").strip()

if not database_url:
    print("\n❌ No URL provided. Exiting.")
    exit(1)

if not database_url.startswith("postgresql://"):
    print("\n❌ Invalid connection string. It should start with 'postgresql://'")
    exit(1)

if "[YOUR-PASSWORD]" in database_url:
    print("\n❌ You forgot to replace [YOUR-PASSWORD] with your actual password!")
    exit(1)

# Read current .env file
try:
    with open('.env', 'r') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("\n❌ .env file not found. Please create it first.")
    exit(1)

# Update DATABASE_URL line
updated = False
new_lines = []
for line in lines:
    if line.startswith('DATABASE_URL='):
        new_lines.append(f'DATABASE_URL={database_url}\n')
        updated = True
    else:
        new_lines.append(line)

# Write back to .env
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("\n✅ SUCCESS! DATABASE_URL has been added to your .env file")
print("\nYou can now test the database connection!")
print("\nRun: python test_database.py")
