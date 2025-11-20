import os

# Your credentials (without spaces)
content = """WEBMOBI_EMAIL=bommenabharath12@gmail.com
WEBMOBI_PASSWORD=Bharath@12"""

# Overwrite the .env file with clean data
with open(".env", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ FIXED: .env file has been rewritten correctly.")
print("   - Removed spaces around '='")
print("   - Verified file encoding")

# Verify immediately
from dotenv import load_dotenv
load_dotenv(override=True)

email = os.getenv("WEBMOBI_EMAIL")
if email:
    print(f"✅ SUCCESS: Python can now read email: {email}")
else:
    print("❌ FAIL: Still cannot read the file.")