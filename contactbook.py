import tkinter as tk  
from tkinter import ttk, messagebox  
import json   
import os, sys 
import random 

def resource_path(relative_path): 
    try:
        base_path = sys._MEIPASS  # Path used by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ===== JSON File Setup =====
DATA_FILE = "contacts.json"

# Load contacts from JSON
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            contacts_list = json.load(f)
            contacts_list = [c if isinstance(c, dict) else json.loads(c) for c in contacts_list]
        except:
            contacts_list = []
else:
    contacts_list = []

# Save contacts to JSON
def save_contacts():
    with open(DATA_FILE, "w") as f:
        json.dump(contacts_list, f, indent=4)

# ===== Address List =====
ADDRESS_LIST = [
    "Balayan, Batangas",
    "Lemery, Batangas",
    "Taal, Batangas",
    "Calaca, Batangas",
    "Nasugbu, Batangas",
    "Manila City, Metro Manila",
    "Quezon City, Metro Manila",
    "Makati City, Metro Manila",
    "Cebu City, Cebu",
    "Davao City, Davao del Sur",
]

# ===== Autocomplete Popup =====
def destroy_addr_popup():  
    if hasattr(root, "addr_popup") and root.addr_popup:
        try:
            root.addr_popup.destroy()
        except:
            pass
        finally:
            if hasattr(root, "addr_popup"):
                delattr = False
                try:
                    del root.addr_popup
                except Exception:
                    pass

def show_address_popup(event=None):
    if event is not None and getattr(event, "keysym", None) in ("Escape",):
        destroy_addr_popup()
        return

    text = address_var.get().strip().lower()
    destroy_addr_popup()

    if not text:
        return

    matches = [addr for addr in ADDRESS_LIST if text in addr.lower()]
    if not matches:
        return

    popup = tk.Toplevel(root)
    popup.wm_overrideredirect(True)
    popup.configure(bg="white", padx=1, pady=1)

    try:
        x = address_entry.winfo_rootx()
        y = address_entry.winfo_rooty() + address_entry.winfo_height()
    except Exception:
        x = root.winfo_rootx() + 50
        y = root.winfo_rooty() + 100

    max_height = 200
    item_height = 28
    height = min(max_height, len(matches) * item_height)
    popup.geometry(f"360x{height}+{x}+{y}")

    for addr in matches:
        lbl = tk.Label(popup, text=addr, anchor="w", padx=6, pady=4)
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e, l=lbl: l.configure(bg="#f0f0f0"))
        lbl.bind("<Leave>", lambda e, l=lbl: l.configure(bg="white"))
        lbl.bind("<Button-1>", lambda e, a=addr: select_address(a))

    root.addr_popup = popup

    def on_root_click(event):
        w = event.widget
        try:
            popup_id = str(popup)
            if str(w).startswith(popup_id):
                return
        except Exception:
            pass
        try:
            if w is address_entry or str(w).startswith(str(address_entry)):
                return
        except Exception:
            pass
        destroy_addr_popup()

    root.bind_all("<Button-1>", on_root_click, add="+")
    root.bind_all("<Key-Escape>", lambda e: destroy_addr_popup(), add="+")

def select_address(address):
    address_var.set(address)
    destroy_addr_popup()

def cleanup_bindings():
    try:
        root.unbind_all("<Button-1>")
        root.unbind_all("<Key-Escape>")
    except Exception:
        pass
    destroy_addr_popup()

# ===== Helper Functions =====
def get_avatar_color(name=None):
    colors = ["#FFCDD2", "#F8BBD0", "#E1BEE7", "#D1C4E9", "#C5CAE9",
              "#BBDEFB", "#B3E5FC", "#B2EBF2", "#B2DFDB", "#C8E6C9"]
    if name:
        return colors[hash(name) % len(colors)]
    return random.choice(colors)

# ===== Contact Functions =====
def add_contact():
    name = name_var.get().strip()
    phone = phone_var.get().strip()
    email = email_var.get().strip()
    address = address_var.get().strip()
    
    if not name:
        messagebox.showwarning("Warning", "Name is required")
        return
    
    global edit_id
    if edit_id is not None:
        for c in contacts_list:
            if c['id'] == edit_id:
                c['name'] = name
                c['phone'] = phone
                c['email'] = email
                c['address'] = address
                break
        edit_id = None
    else:
        new_id = 1
        if contacts_list:
            new_id = max(c['id'] for c in contacts_list) + 1
        contacts_list.append({
            "id": new_id,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address
        })
    save_contacts()
    clear_entries()
    load_contacts()

def delete_contact_by_id(contact_id):
    global contacts_list
    contacts_list = [c for c in contacts_list if c['id'] != contact_id]
    save_contacts()
    load_contacts()

def delete_contact_table():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a contact to delete")
        return
    contact_id = tree.item(selected)['values'][0]
    delete_contact_by_id(contact_id)

def delete_contact_card(contact_id):
    delete_contact_by_id(contact_id)

def edit_contact_by_id(contact_id):
    global edit_id
    for c in contacts_list:
        if c['id'] == contact_id:
            name_var.set(c['name'])
            phone_var.set(c['phone'])
            email_var.set(c['email'])
            address_var.set(c['address'])
            edit_id = contact_id
            notebook.select(card_tab)
            break

def edit_contact_table():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a contact to edit")
        return
    contact_id = tree.item(selected)['values'][0]
    edit_contact_by_id(contact_id)

def edit_contact_card(contact_id):
    edit_contact_by_id(contact_id)

def clear_entries():
    global edit_id
    name_var.set("")
    phone_var.set("")
    email_var.set("")
    address_var.set("")
    edit_id = None
    destroy_addr_popup()

# ===== Rounded Rectangle =====
def round_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

# ===== Load Contacts =====
def load_contacts(event=None):
    search_text = search_var.get().lower()

    # Clear tree
    for row in tree.get_children():
        tree.delete(row)

    # Insert into table
    for idx, contact in enumerate(contacts_list):
        if search_text and search_text not in contact['name'].lower() and search_text not in contact['phone'].lower():
            continue

        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(
            contact['id'],
            contact['name'],
            contact['phone'],
            contact['email'],
            contact['address']
        ), tags=(tag,))

    # Clear phone view
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Phone view cards
    for contact in contacts_list:
        if search_text and search_text not in contact['name'].lower() and search_text not in contact['phone'].lower():
            continue

        contact_id = contact['id']
        name = contact['name']
        phone = contact['phone']
        email = contact['email']
        address = contact['address']

        card_canvas = tk.Canvas(scrollable_frame, width=880, height=100, bg="#cce6ff", highlightthickness=0)
        card_canvas.pack(pady=7)

        card_canvas.create_rectangle(5, 5, 880, 100, fill="#99ccff", outline="", width=0)
        round_rectangle(card_canvas, 0, 0, 875, 95, radius=15, fill="#e6f2ff", outline="")

        avatar_bg = get_avatar_color(name)
        avatar = tk.Canvas(card_canvas, width=50, height=50, bg=avatar_bg, highlightthickness=0)
        avatar.create_text(25, 25, text=name[0].upper(), font=("Arial", 18, "bold"), fill="#ffffff")
        avatar.place(x=15, y=22)

        card_canvas.create_text(80, 25, text=name, anchor="w", font=("Arial", 14, "bold"))
        card_canvas.create_text(80, 50, text=f"📞 {phone}", anchor="w", font=("Arial", 12, "bold"))
        card_canvas.create_text(80, 75, text=f"✉️ {email}   🏠 {address}", anchor="w", font=("Arial", 11), fill="gray")

        tk.Button(card_canvas, text="Edit", bg="#2196F3", fg="white", bd=0, width=6,
                  command=lambda cid=contact_id: edit_contact_card(cid)).place(x=750, y=25)

        tk.Button(card_canvas, text="Delete", bg="#f44336", fg="white", bd=0, width=6,
                  command=lambda cid=contact_id: delete_contact_card(cid)).place(x=750, y=55)

# ===== UI Setup =====
root = tk.Tk()
root.title("Contact Book")

# Desired window size
window_width = 950
window_height = 650

# Get screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Compute center position
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Apply centered geometry
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.configure(bg="#cce6ff")
root.iconbitmap(resource_path("phone.ico"))

name_var = tk.StringVar()
phone_var = tk.StringVar()
email_var = tk.StringVar()
address_var = tk.StringVar()
search_var = tk.StringVar()
edit_id = None

# ===== Search Bar =====
search_frame = tk.Frame(root, bg="#cce6ff")
search_frame.pack(pady=10)
tk.Label(search_frame, text="Search:", bg="#cce6ff", font=("Arial", 12)).pack(side="left")
tk.Entry(search_frame, textvariable=search_var, width=45, font=("Arial", 12), bd=2, relief="groove").pack(side="left", padx=5)
search_var.trace("w", lambda *args: load_contacts())

# ===== Form =====
form_frame = tk.Frame(root, bg="#cce6ff")
form_frame.pack(pady=10)

tk.Label(form_frame, text="Name:", bg="#cce6ff", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
tk.Entry(form_frame, textvariable=name_var, width=45, font=("Arial", 11), bd=2, relief="groove").grid(row=0, column=1, padx=10)

tk.Label(form_frame, text="Phone:", bg="#cce6ff", font=("Arial", 11)).grid(row=1, column=0, sticky="w")
tk.Entry(form_frame, textvariable=phone_var, width=45, font=("Arial", 11), bd=2, relief="groove").grid(row=1, column=1, padx=10)

tk.Label(form_frame, text="Email:", bg="#cce6ff", font=("Arial", 11)).grid(row=2, column=0, sticky="w")
tk.Entry(form_frame, textvariable=email_var, width=45, font=("Arial", 11), bd=2, relief="groove").grid(row=2, column=1, padx=10)

tk.Label(form_frame, text="Address:", bg="#cce6ff", font=("Arial", 11)).grid(row=3, column=0, sticky="w")

address_entry = tk.Entry(form_frame, textvariable=address_var, width=45,
                         font=("Arial", 11), bd=2, relief="groove")
address_entry.grid(row=3, column=1, padx=10)
address_entry.bind("<KeyRelease>", show_address_popup)
address_entry.bind("<FocusOut>", lambda e: root.after(150, destroy_addr_popup))

# ===== Buttons =====
button_frame = tk.Frame(root, bg="#cce6ff")
button_frame.pack(pady=15)

buttons = [
    ("Add / Save", add_contact, "#4CAF50"),
    ("Edit", edit_contact_table, "#2196F3"),
    ("Delete", delete_contact_table, "#f44336"),
    ("Clear", clear_entries, "#FF9800")
]

for i, (text, cmd, color) in enumerate(buttons):
    btn = tk.Button(button_frame, text=text, command=cmd, bg=color, fg="white",
                    width=14, font=("Arial", 11, "bold"))
    btn.grid(row=0, column=i, padx=10)

# ===== Notebook =====
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

# Table view
tree_frame = tk.Frame(notebook)
notebook.add(tree_frame, text="Table View")

tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.pack(side="right", fill="y")

tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Phone", "Email", "Address"),
                    show="headings", yscrollcommand=tree_scroll.set)
tree_scroll.config(command=tree.yview)

for col, w in zip(("ID", "Name", "Phone", "Email", "Address"), (50, 200, 150, 220, 250)):
    tree.heading(col, text=col)
    tree.column(col, width=w)

tree.pack(fill="both", expand=True)

# Card view
card_tab = tk.Frame(notebook, bg="#cce6ff")
notebook.add(card_tab, text="Phone View")

canvas_frame = tk.Frame(card_tab, bg="#cce6ff")
canvas_frame.pack(fill="both", expand=True, pady=10, padx=10)

canvas = tk.Canvas(canvas_frame, bg="#cce6ff", highlightthickness=0)
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#cce6ff")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ===== Initial Load =====
load_contacts()

# ===== Close App =====
root.protocol("WM_DELETE_WINDOW", lambda: (cleanup_bindings(), save_contacts(), root.destroy())) 
root.mainloop()