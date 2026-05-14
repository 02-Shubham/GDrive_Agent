import sys
sys.path.insert(0, ".") # allow importing backend from root
from backend.tools.drive_tool import DriveSearchTool
from datetime import datetime, timedelta
import asyncio

TEST_QUERIES = [
    ("name contains", "name contains 'report'"),
    ("pdf only", "mimeType = 'application/pdf'"),
    ("sheets only", "mimeType = 'application/vnd.google-apps.spreadsheet'"),
    ("full text", "fullText contains 'revenue'"),
    ("last 30 days", f"modifiedTime > '{(datetime.now()-timedelta(days=30)).isoformat()}'"),
    ("name exact", "name = 'README'"),
    ("combined", "name contains 'budget' and mimeType = 'application/pdf'"),
    ("images", "mimeType contains 'image'"),
]

async def main():
    tool = DriveSearchTool()
    print("Testing DriveSearchTool...")
    for name, q in TEST_QUERIES:
        print(f"--- Testing: {name} ---")
        print(f"q param: {q}")
        res = await tool.arun({"q": q})
        print(f"Result length: {len(res)} characters")
        print("Preview: " + res[:200] + ("..." if len(res) > 200 else ""))
        print()

if __name__ == "__main__":
    asyncio.run(main())
