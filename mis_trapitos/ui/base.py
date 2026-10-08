import tkinter as tk
from tkinter import ttk


def add_labeled_entry(parent, text, row, column, width=26, default=""):
    parent.columnconfigure(column + 1, weight=1)
    ttk.Label(parent, text=text).grid(row=row, column=column, sticky="e", padx=(4, 8), pady=5)
    entry = ttk.Entry(parent, width=width)
    entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 10), pady=5)
    if default:
        entry.insert(0, default)
    return entry


def make_tree(parent, columns, height=12):
    container = ttk.Frame(parent)
    container.pack(fill="both", expand=True)
    tree = ttk.Treeview(container, columns=columns, show="headings", height=height)
    yscroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    xscroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    preferred_widths = {
        "id": 58, "codigo": 120, "producto": 190, "producto_id": 85,
        "categoria": 125, "talla": 75, "color": 100, "stock": 75,
        "precio": 105, "proveedor": 145, "nombre": 175, "telefono": 120,
        "correo": 190, "region": 135, "preferencias": 180, "direccion": 210,
        "suministra": 190, "ultimo_pedido": 120, "usuario": 130, "rol": 125,
        "descuento": 100, "inicio": 105, "fin": 105, "cantidad": 90,
        "fecha": 145, "motivo": 210, "venta": 75, "metodo": 165,
        "total": 110, "periodo": 130, "piezas": 90, "ventas": 110,
        "empleado": 170, "costo": 110, "utilidad": 110, "tipo": 125,
        "requerimiento": 420, "modulo": 170, "prueba": 300,
        "elemento": 220, "valor": 260, "estado": 125, "resultado": 220,
        "mensaje": 520,
    }
    for col in columns:
        tree.heading(col, text=col)
        width = preferred_widths.get(col, 130)
        tree.column(col, width=width, minwidth=max(55, min(width, 90)), anchor="w", stretch=True)
    return tree


def tree_clear(tree):
    for item in tree.get_children():
        tree.delete(item)


def set_entries(entries, values):
    for entry, value in zip(entries, values):
        entry.delete(0, tk.END)
        entry.insert(0, "" if value is None else str(value))
