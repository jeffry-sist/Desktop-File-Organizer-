import os 
import shutil
# In below your_username sentance change that to your computer names 
Dowload_folder = r"C:\Users\YOUR_USERNAME\Downloads"
Document_folder = r"C:\Users\YOUR_USERNAME\Documents"
real_files=os.listdir(Dowload_folder)
for file_name in real_files:
    Current_location=os.path.join(Dowload_folder,file_name)
    if file_name.endswith(".pdf"):
        Destination=os.path.join(Document_folder,file_name)
        shutil.move(Current_location,Destination)
        print(f"your {file_name} is moved to Document_folder")
    elif file_name.endswith(".jpg"):
        print("that file was picture so we didnt move that")
    else:
        print("The file has different end name so not found.")