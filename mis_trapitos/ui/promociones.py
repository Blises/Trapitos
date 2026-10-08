import tkinter as tk
from tkinter import messagebox, ttk

from mis_trapitos.data.database import today_text, date_offset
from mis_trapitos.ui.base import add_labeled_entry, make_tree, tree_clear, set_entries


class PromocionesUI(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, padding=10)
        self.db = db
        self.selected_promotion_id = None
        self._build_widgets()

    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="Promocion", padding=10)
        form.pack(fill="x")
        self.pr_product = add_labeled_entry(form, "ID producto", 0, 0)
        self.pr_discount = add_labeled_entry(form, "Descuento %", 0, 2)
        self.pr_start = add_labeled_entry(form, "Inicio", 1, 0, default=today_text())
        self.pr_end = add_labeled_entry(form, "Fin", 1, 2, default=date_offset(30))
        ttk.Button(form, text="Guardar promocion", command=self.save_promotion_ui).grid(
            row=2, column=0, pady=8
        )
        ttk.Button(form, text="Limpiar", command=self.clear_promotion_form).grid(
            row=2, column=1, pady=8
        )
        table = ttk.LabelFrame(self, text="Promociones registradas", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.promotions_tree = make_tree(
            table,
            ("id", "producto_id", "codigo", "producto", "descuento", "inicio", "fin"),
            height=16,
        )
        self.promotions_tree.bind("<<TreeviewSelect>>", self.load_promotion_selected)
        self.refresh_promotions()

    def save_promotion_ui(self):
        try:
            product_id = int(self.pr_product.get())
            discount = float(self.pr_discount.get() or 0)
            if discount < 0 or discount > 100:
                raise ValueError("Descuento no valido.")
            if not self.db.one("SELECT id FROM products WHERE id=?", (product_id,)):
                raise ValueError("Producto no encontrado.")
            self.selected_promotion_id = self.db.save_promotion(
                self.selected_promotion_id,
                product_id,
                discount,
                self.pr_start.get().strip() or today_text(),
                self.pr_end.get().strip() or today_text(),
            )
            self.refresh_promotions()
            messagebox.showinfo("Promociones", "Promocion guardada.")
        except Exception as e:
            messagebox.showerror("Promociones", str(e))

    def refresh_promotions(self):
        rows = self.db.query(
            "SELECT pr.id, pr.product_id AS producto_id, p.code AS codigo, p.name "
            "AS producto, pr.discount_percent AS descuento, pr.start_date AS inicio, "
            "pr.end_date AS fin FROM promotions pr JOIN products p ON p.id=pr.product_id "
            "ORDER BY pr.id DESC"
        )
        tree_clear(self.promotions_tree)
        for row in rows:
            self.promotions_tree.insert("", tk.END, values=[row[key] for key in row.keys()])

    def load_promotion_selected(self, event=None):
        sel = self.promotions_tree.selection()
        if not sel:
            return
        promotion_id = self.promotions_tree.item(sel[0], "values")[0]
        row = self.db.one("SELECT * FROM promotions WHERE id=?", (promotion_id,))
        if not row:
            return
        self.selected_promotion_id = row["id"]
        set_entries(
            [self.pr_product, self.pr_discount, self.pr_start, self.pr_end],
            [row["product_id"], row["discount_percent"], row["start_date"], row["end_date"]],
        )

    def clear_promotion_form(self):
        self.selected_promotion_id = None
        for entry in [self.pr_product, self.pr_discount, self.pr_start, self.pr_end]:
            entry.delete(0, tk.END)
        self.pr_start.insert(0, today_text())
        self.pr_end.insert(0, date_offset(30))
