import tkinter as tk
from tkinter import messagebox, ttk

from mis_trapitos.ui.base import add_labeled_entry, make_tree, tree_clear


class DevolucionesUI(ttk.Frame):
    def __init__(self, parent, db, on_inventario_actualizado=None):
        super().__init__(parent, padding=10)
        self.db = db
        self.on_inventario_actualizado = on_inventario_actualizado
        self._build_widgets()

    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="Registro", padding=10)
        form.pack(fill="x")
        self.r_sale = add_labeled_entry(form, "Venta para devolucion", 0, 0)
        self.r_product = add_labeled_entry(form, "ID producto", 0, 2)
        self.r_quantity = add_labeled_entry(form, "Cantidad", 1, 0, default="1")
        self.r_reason = add_labeled_entry(form, "Motivo devolucion", 1, 2)
        ttk.Button(form, text="Registrar devolucion", command=self.return_item_ui).grid(
            row=2, column=0, pady=8
        )
        self.cancel_sale_entry = add_labeled_entry(form, "Venta a cancelar", 3, 0)
        self.cancel_reason = add_labeled_entry(form, "Motivo cancelacion", 3, 2)
        ttk.Button(form, text="Cancelar venta", command=self.cancel_sale_ui).grid(
            row=4, column=0, pady=8
        )
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)
        returns_frame = ttk.LabelFrame(body, text="Devoluciones", padding=5)
        returns_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.returns_tree = make_tree(
            returns_frame, ("id", "venta", "producto", "cantidad", "fecha", "motivo"), height=14
        )
        cancellations_frame = ttk.LabelFrame(body, text="Cancelaciones", padding=5)
        cancellations_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.cancellations_tree = make_tree(
            cancellations_frame, ("id", "venta", "fecha", "motivo"), height=14
        )
        self.refresh_returns()

    def return_item_ui(self):
        try:
            self.db.return_item(
                int(self.r_sale.get()),
                int(self.r_product.get()),
                int(self.r_quantity.get()),
                self.r_reason.get().strip(),
            )
            self.refresh_returns()
            if self.on_inventario_actualizado is not None:
                self.on_inventario_actualizado()
            messagebox.showinfo("Devolucion", "Devolucion registrada.")
        except Exception as e:
            messagebox.showerror("Devolucion", str(e))

    def cancel_sale_ui(self):
        try:
            self.db.cancel_sale(
                int(self.cancel_sale_entry.get()), self.cancel_reason.get().strip()
            )
            self.refresh_returns()
            if self.on_inventario_actualizado is not None:
                self.on_inventario_actualizado()
            messagebox.showinfo("Cancelacion", "Venta cancelada.")
        except Exception as e:
            messagebox.showerror("Cancelacion", str(e))

    def refresh_returns(self):
        rows = self.db.query(
            "SELECT r.id, r.sale_id AS venta, p.name AS producto, r.quantity AS "
            "cantidad, r.return_datetime AS fecha, r.reason AS motivo "
            "FROM returns r JOIN products p ON p.id=r.product_id ORDER BY r.id DESC"
        )
        tree_clear(self.returns_tree)
        for row in rows:
            self.returns_tree.insert("", tk.END, values=[row[key] for key in row.keys()])
        rows = self.db.query(
            "SELECT id, sale_id AS venta, cancel_datetime AS fecha, reason AS motivo "
            "FROM cancellations ORDER BY id DESC"
        )
        tree_clear(self.cancellations_tree)
        for row in rows:
            self.cancellations_tree.insert("", tk.END, values=[row[key] for key in row.keys()])
