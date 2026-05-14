import sys
sys.path.insert(0, ".") # allow importing backend from root
from backend.tools.drive_tool import list_files_raw

def main():
    print("Testing Drive connection...")
    try:
        # We search for anything by passing a generic query
        files = list_files_raw("name contains ''")
        if not files:
            print("No files found. Check folder ID and sharing permissions.")
        else:
            print(f"Found {len(files)} files:")
            for f in files:
                mimetype = f['mimeType'].split('.')[-1]
                modified_time = f.get('modifiedTime', '?')
                print(f"  [{mimetype}] {f['name']} — {modified_time}")
        print("Connection test complete.")
    except Exception as e:
        print(f"Error connecting to Google Drive: {e}")

if __name__ == "__main__":
    main()
