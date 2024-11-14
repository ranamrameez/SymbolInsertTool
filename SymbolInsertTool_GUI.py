import tkinter as tk
from tkinter import filedialog
import os
import base64
import sqlite3
import json


def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Stylx Files", "*.stylx")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)


def process_symbols():
    symbol_directory = folder_entry.get()
    stylx_path = file_entry.get()

    if not os.path.exists(stylx_path):
        open(stylx_path, "w").close()

    conn = sqlite3.connect(stylx_path, timeout=60)
    cursor = conn.cursor()

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
                3,
                "",
                symbol_name,
                "Landmark Symbol",
                json.dumps(new_symbol_json),
                symbol_name,
            )
            cursor.execute(
                "INSERT INTO ITEMS(CLASS, CATEGORY, NAME, TAGS, CONTENT, KEY) VALUES(?,?,?,?,?,?)",
                new_row,
            )

    conn.commit()
    conn.close()
    result_label.config(text="All symbols have been added to the .stylx file.")


# Setup GUI
root = tk.Tk()
root.title("Symbol Inserter Tool - Load symbols into style file")

folder_label = tk.Label(root, text="\n\nSelect PNG Symbol Directory:")
folder_label.pack()

folder_entry = tk.Entry(root, width=50)
folder_entry.pack()

folder_button = tk.Button(root, text="Browse", command=browse_folder)
folder_button.pack()

file_label = tk.Label(root, text="\nSelect Stylx File:")
file_label.pack()

file_entry = tk.Entry(root, width=50)
file_entry.pack()

file_button = tk.Button(root, text="Browse", command=browse_file)
file_button.pack()

tk.Label(root, text="\n\n").pack()
process_button = tk.Button(root, text="Load PNGs Into Style", command=process_symbols)
process_button.pack()

result_label = tk.Label(root, text="\n")
result_label.pack()

root.mainloop()
