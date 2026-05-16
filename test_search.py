from backend.tools.drive_tool import DriveSearchTool
tool = DriveSearchTool()
print("Search: name contains 'invoice' or fullText contains 'github'")
print(tool._run("name contains 'invoice' or fullText contains 'github'"))
print("Search: name contains 'github invoice'")
print(tool._run("name contains 'github invoice'"))
print("Search: fullText contains 'github invoice'")
print(tool._run("fullText contains 'github invoice'"))
