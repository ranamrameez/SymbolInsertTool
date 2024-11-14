import os
import base64
import sqlite3
import json

# Paths to symbols and new style file
symbol_directory = r"D:\ArcPro Projects\Explore_GIS_Data\ExploreGISDatasets\landamrks_symbology\Landmark_New_Symbols"
stylx_path = r"D:\ArcPro Projects\Explore_GIS_Data\ExploreGISDatasets\styles\landmark_symbols.stylx"

# Initialize the .stylx file
if not os.path.exists(stylx_path):
    open(stylx_path, "w").close()  # Create the file if it doesn't exist

print("Connecting Style DB")
# Connect to the .stylx file as a SQLite database
conn = sqlite3.connect(stylx_path, timeout=60)  # Timeout of 10 seconds

cursor = conn.cursor()
print("Connected.")
# Prepare the table for symbols
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS ITEMS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CLASS INTEGER,
        CATEGORY TEXT,
        NAME TEXT,
        TAGS TEXT,
        CONTENT TEXT,
        KEY TEXT
    )
"""
)

print("Table initiated if not existed.")
print("Inserting symbols into db...")
# Insert symbols from directory into .stylx
for file_name in os.listdir(symbol_directory):
    if file_name.endswith(".png"):
        symbol_name = os.path.splitext(file_name)[0]
        image_path = os.path.join(symbol_directory, file_name)

        # Read and encode the image file
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            encoded_image = base64.b64encode(img_data).decode("utf-8")

        # Define the symbol JSON structure (simple CIMPictureMarker)
        new_symbol_json = {
            "type": "CIMPointSymbol",
            "symbolLayers": [
                {
                    "type": "CIMPictureMarker",
                    "path": image_path,
                    "title": symbol_name,
                    "url": f"data:image/png;base64,{encoded_image}",
                    "size": 20,
                    "enable": "true",
                    "colorLocked": "true",
                    "anchorPointUnits": "Relative",
                    "dominantSizeAxis3D": "Y",
                    "billboardMode3D": "FaceNearPlane",
                    "invertBackfaceTexture": "true",
                    "scaleX": 1,
                    "textureFilter": "Draft",
                }
            ],
        }

        # Generate unique ID and insert into the .stylx file
        new_row = (
            3,  # CLASS (symbol class)
            "",  # CATEGORY
            symbol_name,  # NAME
            "Landmark Symbol",  # TAGS (optional)
            json.dumps(new_symbol_json),  # CONTENT (symbol JSON)
            symbol_name,  # KEY
        )
        cursor.execute(
            # "INSERT INTO ITEMS(ID, CLASS, CATEGORY, NAME, TAGS, CONTENT, KEY) VALUES(?,?,?,?,?,?,?)",
            "INSERT INTO ITEMS(CLASS, CATEGORY, NAME, TAGS, CONTENT, KEY) VALUES(?,?,?,?,?,?)",
            new_row,
        )
        print(f"Inserted symbol: {symbol_name}")

# Commit and close the connection
conn.commit()
conn.close()
print("All symbols have been added to the .stylx file.")