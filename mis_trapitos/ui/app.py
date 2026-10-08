import csv
import hashlib
import os
import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw

from mis_trapitos.ui.productos import IMAGE_DIR, ProductosUI
from mis_trapitos.data.database import (
    Database,
    DB_NAME,
    PAYMENT_METHODS,
    now_text,
    today_text,
    date_offset
)

from mis_trapitos.ui.contactos import ContactosUI
from mis_trapitos.ui.ventas import VentasUI, ServicioVentas

APP_TITLE = "Mis trapitos - Sistema local"
APP_VERSION = "7.0"
DB_NAME = "mis_trapitos.db"
DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
PAYMENT_METHODS = ("Efectivo", "Tarjeta de credito", "Tarjeta de debito", "Transferencia bancaria")

CONFIG_ITEMS = [
    ("CI-01", "Codigo fuente principal", "mis_trapitos_app_v7.py", "Controlado"),
    ("CI-02", "Base de datos local", "mis_trapitos.db", "Controlado"),
    ("CI-03", "Version de aplicacion", APP_VERSION, "Controlado"),
    ("CI-04", "Operacion sin Internet", "SQLite local y Tkinter", "Controlado"),
    ("CI-05", "Usuario inicial", "admin / 1234", "Controlado"),
    ("CI-06", "Modulo de productos", "ui_productos.py", "Controlado"),
    ("CI-07", "Modulo de contactos y usuarios", "ui_contactos.py", "Controlado"),
    ("CI-08", "Modulo de ventas", "ui_ventas.py", "Controlado"),
]

TRACEABILITY = [
    ("RF-01", "Registrar productos con categoria, descripcion, precio, talla y color", "Productos",
"Guardar producto y verificar en inventario"),
    ("RF-02", "Manejar variaciones de talla y color con existencias", "Productos", "Registrar mismo producto con otra talla o color"),
    ("RF-03", "Agregar productos y actualizar cantidades de inventario", "Productos", "Modificar stock y revisar movimiento"),
    ("RF-04", "Actualizar inventario automaticamente al registrar venta", "Ventas", "Vender producto y comprobar disminucion"),
    ("RF-05", "Registrar movimientos de inventario", "Inventario", "Consultar movimientos de entrada, salida, ajuste, devolucion y cancelacion"),
    ("RF-06", "Registrar ventas con productos, cantidades y metodo de pago", "Ventas", "Registrar venta con carrito"),
    ("RF-07", "Registrar pagos en efectivo, tarjeta y transferencia", "Ventas", "Seleccionar metodo de pago"),
    ("RF-08", "Aplicar descuentos a ventas", "Ventas", "Capturar descuento general"),
    ("RF-09", "Registrar promociones con porcentaje y duracion", "Promociones", "Crear promocion vigente"),
    ("RF-10", "Aplicar descuentos automaticos segun condiciones", "Promociones y Ventas", "Venta aplica promocion vigente"),
    ("RF-11", "Registrar clientes con nombre, direccion, correo y telefono", "Clientes", "Guardar cliente"),
    ("RF-12", "Almacenar y consultar historial de compras de cada cliente", "Clientes y Reportes", "Consultar historial"),
    ("RF-13", "Registrar proveedores e informacion de contacto", "Proveedores", "Guardar proveedor"),
    ("RF-14", "Relacionar proveedor con productos que suministra", "Productos y Proveedores", "Consultar productos por proveedor"),
    ("RF-15", "Consultar productos disponibles e inventario por categoria", "Reportes", "Reporte por categoria"),
    ("RF-16", "Consultar productos en oferta y descuentos", "Reportes", "Reporte de productos en oferta"),
    ("RF-17", "Consultar metodos de pago mas utilizados", "Reportes", "Reporte de metodos de pago"),
    ("RF-18", "Consultar productos mas vendidos en el ultimo mes", "Reportes", "Reporte mensual"),
    ("RF-19", "Consultar ventas realizadas en los ultimos tres dias", "Reportes", "Reporte de ultimos tres dias"),
    ("RF-20", "Consultar productos de un proveedor especifico", "Reportes", "Parametro de proveedor"),
    ("RF-21", "Consultar productos comprados mas de una vez por un cliente", "Reportes", "Parametro de cliente"),
    ("RF-22", "Consultar productos vendidos por categoria en el ultimo mes", "Reportes", "Parametro de categoria"),
    ("RF-23", "Consultar productos con precio superior a cierto valor y existencias", "Reportes", "Parametro de precio"),
    ("RF-24", "Consultar producto con mayor descuento vigente", "Reportes", "Promociones vigentes"),
    ("RF-25", "Consultar compras por ciudad o region del cliente", "Reportes", "Agrupar por region"),
    ("RF-26", "Consultar productos no vendidos en los ultimos tres meses", "Reportes", "Reporte sin ventas recientes"),
    ("RNF-01", "Reflejar en tiempo real la disminucion del inventario", "Ventas e Inventario", "Validar stock inmediatamente despues de vender"),
]

REPORTS = [
    "Inventario general actualizado",
    "Productos con stock bajo",
    "Ventas diarias, semanales y mensuales",
    "Ventas por producto",
    "Ventas por metodo de pago",
    "Ventas por empleado",
    "Productos mas vendidos",
    "Productos menos vendidos",
    "Entradas de mercancia",
    "Clientes frecuentes",
    "Resumen de utilidades",
    "Productos devueltos o cancelados",
    "Productos disponibles por categoria",
    "Productos en oferta",
    "Metodos de pago mas utilizados",
    "Productos mas vendidos ultimo mes",
    "Ventas ultimos tres dias",
    "Productos de proveedor especifico",
    "Productos comprados mas de una vez por cliente",
    "Productos vendidos por categoria ultimo mes",
    "Productos con precio superior y existencias",
    "Producto con mayor descuento vigente",
    "Compras por ciudad o region",
    "Productos no vendidos ultimos tres meses",
]



def now_text():
    return datetime.now().strftime(DATETIME_FMT)



def today_text():
    return date.today().strftime(DATE_FMT)



def date_offset(days):
    return (date.today() + timedelta(days=days)).strftime(DATE_FMT)



def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()



def money(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"




class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1280x780")
        self.minsize(1120, 680)
        self.db = Database(DB_NAME)
        self.user = None
        self.productos_ui = None
        self.contactos_ui = None
        self.ventas_ui = None
        self.selected_promotion_id = None
        self.protocol("WM_DELETE_WINDOW"          , self.on_close)

    def on_close(self):
        try:
            self.db.close()
        finally:
            self.destroy()


    def show_main(self):
        self.clear_window()
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text=f"Mis trapitos | Usuario: {self.user['name']} | Rol: {self.user['role']}", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(top, text="Salir", command=self.on_close).pack(side="right")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.make_products_tab(nb)
        self.ventas_ui = VentasUI(nb, self.db, self.user, on_venta_registrada=self.refresh_products)
        nb.add(self.ventas_ui, text="Ventas")
        self.contactos_ui = ContactosUI(nb, self.db)
        nb.add(self.contactos_ui, text="Contactos y usuarios")
        self.make_promotions_tab(nb)
        self.make_returns_tab(nb)
        self.make_reports_tab(nb)
        self.make_traceability_tab(nb)

    def clear_window(self):
        for child in self.winfo_children():
            child.destroy()
        self.productos_ui = None
        self.contactos_ui = None
        self.ventas_ui = None

    def add_labeled_entry(self, parent, text, row, column, width=26, default=""):
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="e", padx=4, pady=3)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, sticky="w", padx=4, pady=3)
        if default:
            entry.insert(0, default)
        return entry

    def make_tree(self, parent, columns, height=12):
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

    def tree_clear(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def set_entries(self, entries, values):
        for entry, value in zip(entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, "" if value is None else str(value))

    def make_products_tab(self, nb):
        self.productos_ui = ProductosUI(nb, self.db)
        nb.add(self.productos_ui, text="Productos")

    def refresh_products(self):
        """Actualiza productos tras una venta, devolucion o cancelacion."""
        if self.productos_ui is not None:
            self.productos_ui.actualizar_inventario()

    def make_promotions_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Promociones")
        form = ttk.LabelFrame(tab, text="Promocion", padding=10)
        form.pack(fill="x")
        self.pr_product = self.add_labeled_entry(form, "ID producto", 0, 0)
        self.pr_discount = self.add_labeled_entry(form, "Descuento %", 0, 2)
        self.pr_start = self.add_labeled_entry(form, "Inicio", 1, 0, default=today_text())
        self.pr_end = self.add_labeled_entry(form, "Fin", 1, 2, default=date_offset(30))
        ttk.Button(form, text="Guardar promocion", command=self.save_promotion_ui).grid(row=2, column=0, pady=8)
        ttk.Button(form, text="Limpiar", command=self.clear_promotion_form).grid(row=2, column=1, pady=8)
        table = ttk.LabelFrame(tab, text="Promociones registradas", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.promotions_tree = self.make_tree(table, ("id", "producto_id", "codigo", "producto", "descuento", "inicio", "fin"), height=16)
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
            self.selected_promotion_id = self.db.save_promotion(self.selected_promotion_id, product_id, discount, self.pr_start.get().strip() or today_text(), self.pr_end.get().strip() or today_text())
            self.refresh_promotions()
            messagebox.showinfo("Promociones", "Promocion guardada.")
        except Exception as e:
            messagebox.showerror("Promociones", str(e))

    def refresh_promotions(self):
        rows = self.db.query("""SELECT pr.id, pr.product_id AS producto_id, p.code AS codigo, p.name
AS producto, pr.discount_percent AS descuento, pr.start_date AS inicio, pr.end_date AS fin FROM
promotions pr JOIN products p ON p.id=pr.product_id ORDER BY pr.id DESC""")
        self.tree_clear(self.promotions_tree)
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
        self.set_entries([self.pr_product, self.pr_discount, self.pr_start, self.pr_end], [row["product_id"], row["discount_percent"], row["start_date"], row["end_date"]])

    def clear_promotion_form(self):
        self.selected_promotion_id = None
        for entry in [self.pr_product, self.pr_discount, self.pr_start, self.pr_end]:
            entry.delete(0, tk.END)
        self.pr_start.insert(0, today_text())
        self.pr_end.insert(0, date_offset(30))

    def make_returns_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Devoluciones y cancelaciones")
        form = ttk.LabelFrame(tab, text="Registro", padding=10)
        form.pack(fill="x")
        self.r_sale = self.add_labeled_entry(form, "Venta para devolucion", 0, 0)
        self.r_product = self.add_labeled_entry(form, "ID producto", 0, 2)
        self.r_quantity = self.add_labeled_entry(form, "Cantidad", 1, 0, default="1")
        self.r_reason = self.add_labeled_entry(form, "Motivo devolucion", 1, 2)
        ttk.Button(form, text="Registrar devolucion", command=self.return_item_ui).grid(row=2, column=0, pady=8)
        self.cancel_sale_entry = self.add_labeled_entry(form, "Venta a cancelar", 3, 0)
        self.cancel_reason = self.add_labeled_entry(form, "Motivo cancelacion", 3, 2)
        ttk.Button(form, text="Cancelar venta", command=self.cancel_sale_ui).grid(row=4, column=0, pady=8)
        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, pady=8)
        returns_frame = ttk.LabelFrame(body, text="Devoluciones", padding=5)
        returns_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.returns_tree = self.make_tree(returns_frame, ("id", "venta", "producto", "cantidad", "fecha", "motivo"), height=14)
        cancellations_frame = ttk.LabelFrame(body, text="Cancelaciones", padding=5)
        cancellations_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.cancellations_tree = self.make_tree(cancellations_frame, ("id", "venta", "fecha", "motivo"), height=14)
        self.refresh_returns()

    def return_item_ui(self):
        try:
            self.db.return_item(int(self.r_sale.get()), int(self.r_product.get()), int(self.r_quantity.get()), self.r_reason.get().strip())
            self.refresh_returns()
            self.refresh_products()
            messagebox.showinfo("Devolucion", "Devolucion registrada.")
        except Exception as e:
            messagebox.showerror("Devolucion", str(e))

    def cancel_sale_ui(self):
        try:
            self.db.cancel_sale(int(self.cancel_sale_entry.get()), self.cancel_reason.get().strip())
            self.refresh_returns()
            self.refresh_products()
            messagebox.showinfo("Cancelacion", "Venta cancelada.")
        except Exception as e:
            messagebox.showerror("Cancelacion", str(e))

    def refresh_returns(self):
        rows = self.db.query("""SELECT r.id, r.sale_id AS venta, p.name AS producto, r.quantity AS
cantidad, r.return_datetime AS fecha, r.reason AS motivo FROM returns r JOIN products p ON
p.id=r.product_id ORDER BY r.id DESC""")
        self.tree_clear(self.returns_tree)
        for row in rows:
            self.returns_tree.insert("", tk.END, values=[row[key] for key in row.keys()])
        rows = self.db.query("SELECT id, sale_id AS venta, cancel_datetime AS fecha, reason AS motivo FROM cancellations ORDER BY id DESC")
        self.tree_clear(self.cancellations_tree)
        for row in rows:
            self.cancellations_tree.insert("", tk.END, values=[row[key] for key in row.keys()])

    def make_reports_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Reportes")
        controls = ttk.LabelFrame(tab, text="Consulta", padding=10)
        controls.pack(fill="x")
        ttk.Label(controls, text="Reporte").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.report_combo = ttk.Combobox(controls, values=REPORTS, state="readonly", width=48)
        self.report_combo.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        self.report_combo.set(REPORTS[0])
        self.report_param = self.add_labeled_entry(controls, "Parametro", 0, 2, width=30)
        ttk.Button(controls, text="Ejecutar", command=self.run_report).grid(row=0, column=4, padx=4, pady=4)
        ttk.Button(controls, text="Exportar CSV", command=self.export_report_csv).grid(row=0, column=5, padx=4, pady=4)
        self.report_hint = ttk.Label(controls, text="Parametro se usa en reportes por categoria, proveedor, cliente, precio o stock bajo.")
        self.report_hint.grid(row=1, column=0, columnspan=6, sticky="w", padx=4)
        table = ttk.LabelFrame(tab, text="Resultado", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.report_tree = self.make_tree(table, ("resultado",), height=18)
        self.last_report_rows = []
        self.run_report()

    def run_report(self):
        try:
            rows = self.db.report(self.report_combo.get(), self.report_param.get())
            self.last_report_rows = rows
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            if not rows:
                self.report_tree["columns"] = ("mensaje",)
                self.report_tree.heading("mensaje", text="mensaje")
                self.report_tree.column("mensaje", width=900)
                self.report_tree.insert("", tk.END, values=("Sin resultados",))
                return
            columns = list(rows[0].keys())
            self.report_tree["columns"] = columns
            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=140, anchor="w")
            for row in rows:
                self.report_tree.insert("", tk.END, values=[row[col] for col in columns])
        except Exception as e:
            messagebox.showerror("Reporte", str(e))

    def export_report_csv(self):
        rows = self.last_report_rows
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if rows:
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow([row[key] for key in row.keys()])
        messagebox.showinfo("Exportar", f"Reporte exportado en:\n{path}")

    def make_traceability_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Rastreabilidad")
        upper = ttk.LabelFrame(tab, text="Administracion de configuracion", padding=5)
        upper.pack(fill="x")
        config_tree = self.make_tree(upper, ("id", "elemento", "valor", "estado"), height=5)
        for item in CONFIG_ITEMS:
            config_tree.insert("", tk.END, values=item)
        lower = ttk.LabelFrame(tab, text="Matriz de rastreabilidad", padding=5)
        lower.pack(fill="both", expand=True, pady=8)
        trace_tree = self.make_tree(lower, ("id", "requerimiento", "modulo", "prueba"), height=18)
        for item in TRACEABILITY:
            trace_tree.insert("", tk.END, values=item)
        ttk.Button(tab, text="Ejecutar pruebas basicas", command=self.run_basic_tests).pack(anchor="w", pady=5)

    def run_basic_tests(self):
        try:
            product = self.db.one("SELECT * FROM products ORDER BY stock DESC LIMIT 1")
            employee = self.db.one("SELECT * FROM employees ORDER BY id LIMIT 1")
            customer = self.db.one("SELECT * FROM customers ORDER BY id LIMIT 1")
            if not product or not employee:
                raise ValueError("Faltan productos o empleados para probar.")
            initial_stock = int(product["stock"])
            if initial_stock < 1:
                raise ValueError("No hay stock suficiente para la prueba.")
            servicio = ServicioVentas(self.db)
            servicio.agregar_producto(product["code"], 1)
            sale_id = servicio.registrar_venta(customer["id"] if customer else None, employee["id"], PAYMENT_METHODS[0], 0).sale_id
            after = self.db.scalar("SELECT stock FROM products WHERE id=?", (product["id"],))
            movement = self.db.one("SELECT id FROM inventory_movements WHERE related_sale_id=? AND movement_type='SALIDA'", (sale_id,))
            if after != initial_stock - 1 or not movement:
                raise ValueError("La prueba de inventario no paso.")
            self.refresh_products()
            messagebox.showinfo("Pruebas", f"Pruebas correctas. Venta de prueba: {sale_id}. Stock {initial_stock} -> {after}.")
        except Exception as e:
            messagebox.showerror("Pruebas", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()