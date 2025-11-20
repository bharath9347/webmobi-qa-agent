import os

print("--- DIAGNOSTIC START ---")
try:
    with open(".env", "r") as f:
        lines = f.readlines()
        print(f"Found {len(lines)} lines in .env file.")
        
        for i, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line:
                continue
            
            if "=" in clean_line:
                key, value = clean_line.split("=", 1)
                # Print the KEY but hide the PASSWORD
                masked_value = "*****" if "PASSWORD" in key else value
                print(f"Line {i+1}: Key=['{key.strip()}'] Value=['{masked_value.strip()}']")
            else:
                print(f"❌ Line {i+1} is INVALID: '{clean_line}' (Missing '=')")
except FileNotFoundError:
    print("❌ CRITICAL: .env file does not exist in this folder.")
except Exception as e:
    print(f"❌ ERROR reading file: {e}")

print("--- DIAGNOSTIC END ---")