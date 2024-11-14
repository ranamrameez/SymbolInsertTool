import arcpy
import os
import base64
import sqlite3
import json

class SymbolInsertTool(object):
    def __init__(self):
        """Define the tool (parameters)."""
        self.label = "Insert Symbols into Stylx"
        self.description = "This tool inserts PNG symbols into a .stylx file."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        param0 = arcpy.Parameter(
            displayName="Symbol Directory",
            name="symbol_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        
        param1 = arcpy.Parameter(
            displayName="Stylx File",
            name="stylx_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        
        return [param0, param1]

    def execute(self, parameters, messages):
        """Execute the tool."""
        symbol_directory = parameters[0].valueAsText
        stylx_path = parameters[1].valueAsText
        
        if not os.path.exists(stylx_path):
            open(stylx_path, "w").close()

        conn = sqlite3.connect(stylx_path, timeout=60)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ITEMS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CLASS INTEGER,
                CATEGORY TEXT,
                NAME TEXT,
                TAGS TEXT,
                CONTENT TEXT,
                KEY TEXT
            )
        """)

        for file_name in os.listdir(symbol_directory):
            if file_name.endswith(".png"):
                symbol_name = os.path.splitext(file_name)[0]
                image_path = os.path.join(symbol_directory, file_name)

                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                    encoded_image = base64.b64encode(img_data).decode("utf-8")

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

                new_row = (
                    3, "", symbol_name, "Landmark Symbol", json.dumps(new_symbol_json), symbol_name
                )
                cursor.execute("INSERT INTO ITEMS(CLASS, CATEGORY, NAME, TAGS, CONTENT, KEY) VALUES(?,?,?,?,?,?)", new_row)
                messages.addMessage(f"Inserted symbol: {symbol_name}")

        conn.commit()
        conn.close()
        messages.addMessage("All symbols have been added to the .stylx file.")
