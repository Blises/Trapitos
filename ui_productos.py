"""Interfaz modular de productos, variantes e inventario de Mis Trapitos.

Recibe la base de datos abierta por la aplicación. No crea conexiones ni
importa el punto de entrada; las transacciones siguen a cargo de Database.
"""

import csv
import os
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps, ImageTk


IMAGE_DIR = "mis_trapitos_imagenes"


class ProductosUI(ttk.Frame):
    """Pestaña de productos con estado propio y actualización explícita."""

    def __init__(self, parent, db):
        super().__init__(parent, padding=10)
        self.db = db
        self.selected_product_id = None
        self.product_photo_ref = None
        self._loaded_stock = None
        self._build_widgets()
        self.actualizar_inventario()

    def _build_widgets(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.LabelFrame(self, text="Foto del producto", padding=10)
        right.pack(side="right", fill="y", padx=(10, 0))
        form = ttk.LabelFrame(left, text="Producto", padding=10)
        form.pack(fill="x")
        self.p_code = self._add_labeled_entry(form, "Codigo", 0, 0)
        self.p_name = self._add_labeled_entry(form, "Nombre", 0, 2)
        self.p_category = self._add_labeled_entry(form, "Categoria", 1, 0)
        self.p_size = self._add_labeled_entry(form, "Talla", 1, 2)
        self.p_color = self._add_labeled_entry(form, "Color", 2, 0)
        self.p_purchase = self._add_labeled_entry(form, "Precio compra", 2, 2)
        self.p_sale = self._add_labeled_entry(form, "Precio venta", 3, 0)
        self.p_stock = self._add_labeled_entry(form, "Stock", 3, 2)
        self.p_supplier = self._add_labeled_entry(form, "ID proveedor", 4, 0)
        self.p_entry = self._add_labeled_entry(
            form, "Fecha ingreso", 4, 2, default=date.today().isoformat()
        )
        self.p_brand = self._add_labeled_entry(form, "Marca", 5, 0)
        self.p_season = self._add_labeled_entry(form, "Temporada", 5, 2)
        self.p_image = self._add_labeled_entry(form, "Foto", 6, 0, width=58)
        ttk.Button(form, text="Seleccionar foto", command=self.choose_product_image).grid(
            row=6, column=2, pady=4
        )
        ttk.Button(form, text="Agregar producto", command=self.add_product_ui).grid(
            row=7, column=0, pady=8
        )
        ttk.Button(form, text="Editar producto", command=self.edit_product_ui).grid(
            row=7, column=1, pady=8
        )
        ttk.Button(form, text="Limpiar", command=self.clear_product_form).grid(
            row=7, column=2, pady=8
        )
        ttk.Button(form, text="Ver foto", command=self.show_selected_product_image).grid(
            row=7, column=3, pady=8
        )
        ttk.Button(form, text="Exportar inventario", command=self.export_inventory_csv).grid(
            row=8, column=0, pady=8
        )
        self.product_image_label = tk.Label(
            right, text="Selecciona un producto", anchor="center", width=34,
            height=16, relief="groove", bg="white"
        )
        self.product_image_label.pack(padx=10, pady=10)
        self.product_image_text = ttk.Label(right, text="", wraplength=240, justify="center")
        self.product_image_text.pack(padx=10, pady=5)
        table = ttk.LabelFrame(left, text="Inventario", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.products_tree = self._make_tree(
            table,
            ("id", "codigo", "producto", "categoria", "talla", "color", "stock", "precio", "proveedor"),
            height=15,
        )
        self.products_tree.bind("<<TreeviewSelect>>", self.load_product_selected)

    @staticmethod
    def _add_labeled_entry(parent, text, row, column, width=26, default=""):
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="e", padx=4, pady=3)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, sticky="w", padx=4, pady=3)
        if default:
            entry.insert(0, default)
        return entry

    @staticmethod
    def _make_tree(parent, columns, height=12):
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
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="w")
        return tree

    def choose_product_image(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar foto del producto",
            filetypes=[
                ("Imagenes", ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.ppm", "*.pgm")),
                ("JPG", ("*.jpg", "*.jpeg")), ("PNG", "*.png"), ("Todos", "*.*"),
            ],
        )
        if not path:
            return
        try:
            stored_path = self.store_product_image(path)
            self.p_image.delete(0, tk.END)
            self.p_image.insert(0, stored_path)
            self.display_image(stored_path)
        except Exception as e:
            messagebox.showerror("Foto", str(e), parent=self)

    @staticmethod
    def resolve_image_path(path):
        if not path:
            return ""
        path = path.strip().strip('"')
        if os.path.exists(path):
            return path
        base = os.path.dirname(os.path.abspath(__file__))
        alternative = os.path.join(base, path)
        return alternative if os.path.exists(alternative) else ""

    def store_product_image(self, source_path):
        source_path = self.resolve_image_path(source_path) or source_path
        if not os.path.exists(source_path):
            raise ValueError("No se encontro la imagen seleccionada.")
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), IMAGE_DIR)
        os.makedirs(base, exist_ok=True)
        name, ext = os.path.splitext(os.path.basename(source_path))
        ext = ext.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".ppm", ".pgm"):
            ext = ".jpg"
        safe = "".join(ch for ch in name if ch.isalnum() or ch in ("_", "-")).strip() or "producto"
        target = os.path.join(base, f"{safe}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
        with Image.open(source_path) as source:
            img = ImageOps.exif_transpose(source)
            if ext in (".jpg", ".jpeg"):
                img.convert("RGB").save(target, "JPEG", quality=92)
            elif ext == ".png":
                img.save(target, "PNG")
            else:
                img.save(target)
        return target

    def create_photo_image(self, path, size):
        resolved = self.resolve_image_path(path)
        if not resolved:
            raise ValueError("No hay archivo de imagen disponible.")
        with Image.open(resolved) as source:
            img = ImageOps.exif_transpose(source)
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img.thumbnail(size, resample)
            return ImageTk.PhotoImage(img, master=self), resolved

    def display_image(self, path):
        if not path:
            self.product_photo_ref = None
            self.product_image_label.configure(image="", text="Sin foto", bg="white")
            self.product_image_text.configure(text="No hay archivo de imagen disponible.")
            return
        try:
            photo, resolved = self.create_photo_image(path, (260, 260))
            self.product_photo_ref = photo
            self.product_image_label.configure(image=photo, text="", bg="white")
            self.product_image_text.configure(text=os.path.basename(resolved))
        except Exception as e:
            self.product_photo_ref = None
            self.product_image_label.configure(image="", text="No se pudo mostrar la foto", bg="white")
            self.product_image_text.configure(text=str(e))

    def show_selected_product_image(self):
        path = self.p_image.get().strip()
        if not path:
            messagebox.showwarning("Foto", "Primero selecciona una foto o un producto con foto.", parent=self)
            return
        self.display_image(path)
        try:
            photo, resolved = self.create_photo_image(path, (620, 620))
            window = tk.Toplevel(self)
            window.title(os.path.basename(resolved))
            window.geometry("700x700")
            frame = ttk.Frame(window, padding=12)
            frame.pack(fill="both", expand=True)
            label = tk.Label(frame, image=photo, bg="white")
            label.image = photo
            label.pack(expand=True)
            ttk.Label(frame, text=resolved, wraplength=650, justify="center").pack(pady=8)
        except Exception as e:
            messagebox.showerror("Foto", str(e), parent=self)

    def collect_product_data(self):
        data = (
            self.p_code.get().strip(),
            self.p_name.get().strip(),
            self.p_category.get().strip(),
            self.p_size.get().strip(),
            self.p_color.get().strip(),
            float(self.p_purchase.get() or 0),
            float(self.p_sale.get() or 0),
            int(self.p_stock.get() or 0),
            int(self.p_supplier.get()) if self.p_supplier.get().strip() else None,
            self.p_entry.get().strip() or date.today().isoformat(),
            self.p_brand.get().strip(),
            self.p_season.get().strip(),
            self.p_image.get().strip(),
        )
        if not all(data[:5]):
            raise ValueError("Codigo, nombre, categoria, talla y color son obligatorios.")
        if data[5] < 0 or data[6] < 0 or data[7] < 0:
            raise ValueError("Precios y stock no pueden ser negativos.")
        if data[8] is not None and not self.db.one("SELECT id FROM suppliers WHERE id=?", (data[8],)):
            raise ValueError(
                "El proveedor indicado no existe. Selecciona un ID de proveedor registrado o deja el campo vacio."
            )
        return data

    def add_product_ui(self):
        try:
            data = self.collect_product_data()
            self.selected_product_id = self.db.save_product(None, data)
            self.actualizar_inventario()
            self.products_tree.selection_set(str(self.selected_product_id))
            self.display_image(data[12])
            messagebox.showinfo("Productos", "Producto agregado.", parent=self)
        except Exception as e:
            messagebox.showerror("Productos", str(e), parent=self)

    def edit_product_ui(self):
        try:
            if not self.selected_product_id:
                raise ValueError("Selecciona un producto de la tabla antes de editarlo.")
            data = self.collect_product_data()
            self.db.save_product(self.selected_product_id, data)
            self.actualizar_inventario()
            self.display_image(data[12])
            messagebox.showinfo("Productos", "Producto editado correctamente.", parent=self)
        except Exception as e:
            messagebox.showerror("Productos", str(e), parent=self)

    def save_product_ui(self):
        if self.selected_product_id:
            self.edit_product_ui()
        else:
            self.add_product_ui()

    def actualizar_inventario(self):
        """Refresca existencias confirmadas sin perder selección ni otras ediciones.

        App llama este método después de ventas, devoluciones y cancelaciones.
        Solo se sustituye el stock del formulario si cambió en la base de datos.
        """
        rows = self.db.query(
            """SELECT p.id, p.code AS codigo, p.name AS producto, p.category AS categoria,
                      p.size AS talla, p.color, p.stock, p.sale_price AS precio,
                      COALESCE(s.name,'') AS proveedor
               FROM products p LEFT JOIN suppliers s ON s.id=p.supplier_id
               ORDER BY p.id DESC"""
        )
        stale_items = set(self.products_tree.get_children())
        selected_stock = None
        for index, row in enumerate(rows):
            item_id = str(row["id"])
            values = [row[key] for key in row.keys()]
            if self.products_tree.exists(item_id):
                self.products_tree.item(item_id, values=values)
                self.products_tree.move(item_id, "", index)
            else:
                self.products_tree.insert("", index, iid=item_id, values=values)
            stale_items.discard(item_id)
            if row["id"] == self.selected_product_id:
                selected_stock = int(row["stock"])
        for item_id in stale_items:
            self.products_tree.delete(item_id)
        if self.selected_product_id is not None:
            if selected_stock is None:
                self.clear_product_form()
            elif selected_stock != self._loaded_stock:
                self.p_stock.delete(0, tk.END)
                self.p_stock.insert(0, str(selected_stock))
                self._loaded_stock = selected_stock

    def load_product_selected(self, event=None):
        selection = self.products_tree.selection()
        if not selection:
            return
        product_id = self.products_tree.item(selection[0], "values")[0]
        row = self.db.one("SELECT * FROM products WHERE id=?", (product_id,))
        if not row:
            return
        self.selected_product_id = row["id"]
        self._loaded_stock = int(row["stock"])
        values = [
            row["code"], row["name"], row["category"], row["size"], row["color"],
            row["purchase_price"], row["sale_price"], row["stock"], row["supplier_id"],
            row["entry_date"], row["brand"], row["season"], row["image_path"],
        ]
        for entry, value in zip(self._product_entries(), values):
            entry.delete(0, tk.END)
            entry.insert(0, "" if value is None else str(value))
        self.display_image(row["image_path"])

    def _product_entries(self):
        return (
            self.p_code, self.p_name, self.p_category, self.p_size, self.p_color,
            self.p_purchase, self.p_sale, self.p_stock, self.p_supplier,
            self.p_entry, self.p_brand, self.p_season, self.p_image,
        )

    def clear_product_form(self):
        self.selected_product_id = None
        self._loaded_stock = None
        self.products_tree.selection_remove(self.products_tree.selection())
        for entry in self._product_entries():
            entry.delete(0, tk.END)
        self.p_supplier.insert(0, "1")
        self.p_entry.insert(0, date.today().isoformat())
        self.display_image("")

    def export_inventory_csv(self):
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        rows = self.db.report("Inventario general actualizado")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if rows:
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow([row[key] for key in row.keys()])
        messagebox.showinfo("Exportar", f"Inventario exportado en:\n{path}", parent=self)
