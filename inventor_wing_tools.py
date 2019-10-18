from inventor_connection import inventor, InventorPart
from inventor_parametric_wing import InventorWingSegment
import tkinter as tk
from tkinter import filedialog

def update_active():
    inventor.application.SilentOperation=True
    wing_part = InventorPart(inventor.active_part_document)
    _segment = InventorWingSegment.update_part(wing_part)
    inventor.application.SilentOperation=False

def new_from_template():
    inventor.application.SilentOperation=True
    _segment = InventorWingSegment.create_from_template(
        filedialog.asksaveasfilename(defaultextension=".ipt")
    )
    _segment.populate_template()
    _segment.part.part_doc.Save()
    inventor.application.SilentOperation=False

def show_user_form():
    root = tk.Tk()

    b1 = tk.Button(root, text="Update Active", command=update_active)
    b1.pack()
    b2 = tk.Button(root, text="New From Template", command=new_from_template)
    b2.pack()
    tk.mainloop()

if __name__ == "__main__":
    show_user_form()
