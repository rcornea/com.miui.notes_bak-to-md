# 0.1 - this script works if you use v5.x.x of miui.notes app
# the adb backup contains a sqlite.db which we can process 
import sqlite3
import os
import shutil
import re

# Configuration
db_path = 'apps/com.miui.notes/db/note.db'  # Path to the database
files_dir = 'apps/com.miui.notes/f/'        # Path to image files (adjust if different)
output_dir = 'exported_notes'               # Output directory for Markdown files
images_output_dir = os.path.join(output_dir, 'images')  # Subdirectory for images

# Create output directories
os.makedirs(output_dir, exist_ok=True)
os.makedirs(images_output_dir, exist_ok=True)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all notes (adjust column names as needed)
cursor.execute("SELECT id, title, content, created_date FROM notes")
notes = cursor.fetchall()

for note in notes:
    note_id, title, content, created_date = note

    # Sanitize title for filename, fallback to ID if title is empty
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title.strip()) if title else str(note_id)
    filename = f"{safe_title}.md"
    filepath = os.path.join(output_dir, filename)

    # Write Markdown file
    with open(filepath, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# {title or 'Untitled'}\n\n")
        md_file.write(f"**Created on:** {created_date}\n\n")
        md_file.write(content)

    # Extract and copy image references from content
    image_refs = re.findall(r'!\[\]\((.*?)\)', content)  # Matches ![](image.jpg)
    for image_ref in image_refs:
        image_name = os.path.basename(image_ref)
        src_path = os.path.join(files_dir, image_name)
        dest_path = os.path.join(images_output_dir, image_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            # Update relative path in content if needed (optional)
            # content = content.replace(image_ref, f"images/{image_name}")

# Close database connection
conn.close()

print(f"Notes exported to '{output_dir}' with images in '{images_output_dir}'.")
