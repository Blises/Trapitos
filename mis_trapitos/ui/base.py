import tkinter as tk
from tkinter import font, ttk

from mis_trapitos.ui.styles import UI_COLORS


class FormGrid(ttk.Frame):
    def __init__(self, parent, columns=2, min_column_width=220):
        super().__init__(parent)
        self.max_columns = columns
        self.min_column_width = min_column_width
        self.fields = []
        self._columns = 0
        self.bind("<Configure>", self._reflow)

    def _field(self, label):
        cell = ttk.Frame(self)
        ttk.Label(cell, text=label, style="Field.TLabel").pack(anchor="w", pady=(0, 4))
        self.fields.append(cell)
        self._columns = 0
        return cell

    def add_field(self, label, default="", show=""):
        cell = self._field(label)
        entry = ttk.Entry(cell, width=1, show=show)
        entry.pack(fill="x")
        if default != "":
            entry.insert(0, default)
        self._reflow()
        return entry

    def add_combo(self, label, values, state="readonly"):
        cell = self._field(label)
        combo = ttk.Combobox(cell, values=values, state=state, width=1)
        combo.pack(fill="x")
        self._reflow()
        return combo

    def _reflow(self, event=None):
        width = self.winfo_width()
        scale = self.winfo_fpixels("1i") / 96
        columns = self.max_columns if width <= 1 else max(1, min(self.max_columns, int(width / (self.min_column_width * scale))))
        if columns == self._columns:
            return
        for column in range(self.max_columns):
            self.columnconfigure(column, weight=1 if column < columns else 0, uniform="field" if column < columns else "")
        for i, cell in enumerate(self.fields):
            cell.grid(row=i // columns, column=i % columns, sticky="ew",
                      padx=(0, 16 if i % columns < columns - 1 else 0), pady=(0, 12))
        self._columns = columns


class ActionBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=40)
        self.buttons = []
        self.bind("<Configure>", self._reflow)

    def add(self, text, command, style="TButton"):
        button = ttk.Button(self, text=text, command=command, style=style)
        self.buttons.append(button)
        self._reflow()
        return button

    def _reflow(self, event=None):
        available = self.winfo_width()
        if available <= 1:
            available = 1000
        x = y = height = 0
        for button in self.buttons:
            width = min(available, button.winfo_reqwidth())
            button_height = button.winfo_reqheight()
            if x and x + width > available:
                x = 0
                y += height + 8
                height = 0
            button.place(x=x, y=y, width=width, height=button_height)
            x += width + 8
            height = max(height, button_height)
        self.configure(height=y + height)


class ScrollablePage(ttk.Frame):
    def __init__(self, parent, padding=0):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=UI_COLORS["background"], highlightthickness=0, borderwidth=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self._content = ttk.Frame(self.canvas)
        self._content.columnconfigure(0, weight=1)
        self._content.rowconfigure(0, weight=1)
        self.body = ttk.Frame(self._content, padding=padding)
        self.body.grid(row=0, column=0, sticky="nsew")
        self._window = self.canvas.create_window(0, 0, window=self._content, anchor="nw")
        self.canvas.bind("<Configure>", self._resize)
        self._content.bind("<Configure>", self._resize)

    def _resize(self, event=None):
        width = self.canvas.winfo_width()
        viewport = self.canvas.winfo_height()
        self._content.rowconfigure(0, minsize=viewport)
        self.canvas.itemconfigure(self._window, width=width)
        height = max(viewport, self._content.winfo_reqheight())
        self.canvas.configure(scrollregion=(0, 0, width, height))
        if height > viewport + 1:
            self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))
        else:
            self.scrollbar.grid_remove()
            self.canvas.yview_moveto(0)

    def reveal(self, widget):
        self.update_idletasks()
        top = widget.winfo_rooty() - self.body.winfo_rooty()
        bottom = top + widget.winfo_height()
        visible_top = self.canvas.canvasy(0)
        height = self.body.winfo_height()
        viewport = self.canvas.winfo_height()
        if top < visible_top:
            self.canvas.yview_moveto(max(0, top - 8) / height)
        elif bottom > visible_top + viewport:
            self.canvas.yview_moveto((bottom - viewport + 8) / height)


def handle_page_event(event):
    widget = event.widget
    if not isinstance(widget, tk.Widget):
        return
    if event.type == tk.EventType.MouseWheel and widget.winfo_class() in ("Text", "Treeview", "TCombobox"):
        return
    page = widget
    while page is not None and not isinstance(page, ScrollablePage):
        page = getattr(page, "master", None)
    if page is not None:
        if event.type == tk.EventType.MouseWheel:
            if page.scrollbar.winfo_ismapped():
                page.canvas.yview_scroll(-int(event.delta / 120), "units")
        else:
            page.reveal(widget)


class DataTable(ttk.Treeview):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._stripe_after_id = None
        self.tag_configure("even", background="#FFFFFF")
        self.tag_configure("odd", background="#F4F7FA")
        self.bind("<Destroy>", self._cancel_stripes, add="+")

    def insert(self, parent, index, iid=None, **kwargs):
        item = super().insert(parent, index, iid=iid, **kwargs)
        self._schedule_stripes()
        return item

    def move(self, item, parent, index):
        super().move(item, parent, index)
        self._schedule_stripes()

    reattach = move

    def delete(self, *items):
        super().delete(*items)
        self._schedule_stripes()

    def detach(self, *items):
        super().detach(*items)
        self._schedule_stripes()

    def set_children(self, item, *newchildren):
        super().set_children(item, *newchildren)
        self._schedule_stripes()

    def _schedule_stripes(self):
        if self._stripe_after_id is None:
            self._stripe_after_id = self.after_idle(self._refresh_stripes)

    def _refresh_stripes(self):
        self._stripe_after_id = None
        parents = [""]
        while parents:
            children = self.get_children(parents.pop())
            for index, item in enumerate(children):
                current_tags = self.item(item, "tags")
                tags = tuple(tag for tag in current_tags if tag not in ("even", "odd"))
                tags += ("odd" if index % 2 else "even",)
                if tags != current_tags:
                    self.item(item, tags=tags)
            parents.extend(children)

    def _cancel_stripes(self, event):
        if event.widget is self and self._stripe_after_id is not None:
            self.after_cancel(self._stripe_after_id)
            self._stripe_after_id = None


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
    tree = DataTable(container, columns=columns, show="headings", height=height)
    yscroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    xscroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    configure_tree_columns(tree, columns)
    return tree


def configure_tree_columns(tree, columns):
    tree.configure(columns=columns)
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
    titles = {
        "id": "ID", "codigo": "Código", "categoria": "Categoría",
        "telefono": "Teléfono", "region": "Región", "direccion": "Dirección",
        "producto_id": "ID producto", "ultimo_pedido": "Último pedido",
        "metodo": "Método", "modulo": "Módulo",
    }
    numeric_columns = {
        "id", "stock", "precio", "cantidad", "subtotal", "total",
        "descuento", "costo", "utilidad",
    }
    heading_font = font.Font(root=tree, family="Segoe UI", size=9, weight="bold")
    scale = tree.winfo_fpixels("1i") / 96
    for col in columns:
        title = titles.get(col, col.replace("_", " ").capitalize())
        tree.heading(col, text=title)
        width = max(round(preferred_widths.get(col, 130) * scale), heading_font.measure(title) + 28)
        tree.column(
            col, width=width, minwidth=width,
            anchor="e" if col in numeric_columns else "w", stretch=True,
        )


def tree_clear(tree):
    for item in tree.get_children():
        tree.delete(item)


def set_entries(entries, values):
    for entry, value in zip(entries, values):
        entry.delete(0, tk.END)
        entry.insert(0, "" if value is None else str(value))
