import csv
import hashlib
import os
import sqlite3
import tkinter as tk
import urllib.parse
import webbrowser
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw

from ui_productos import IMAGE_DIR, ProductosUI
from db import (
    Database,
    DB_NAME,
    PAYMENT_METHODS,
    now_text,
    today_text,
    date_offset
)
APP_TITLE = "Mis trapitos - Sistema local"
APP_VERSION = "7.0"
DB_NAME = "mis_trapitos.db"
DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
PAYMENT_METHODS = ("Efectivo", "Tarjeta de credito", "Tarjeta de debito", "Transferencia bancaria")

CONFIG_ITEMS = [
    ("CI-01", "Codigo fuente principal"        , "mis_trapitos_app_v7.py", "Controlado"),
    ("CI-02", "Base de datos local"        , "mis_trapitos.db", "Controlado"),
    ("CI-03", "Version de aplicacion", APP_VERSION, "Controlado"),
    ("CI-04", "Operacion sin Internet"         , "SQLite local y Tkinter", "Controlado"),
    ("CI-05", "Usuario inicial", "admin / 1234", "Controlado"),
    ("CI-06", "Modulo de productos", "ui_productos.py", "Controlado"),
]

TRACEABILITY = [
    ("RF-01", "Registrar productos con categoria, descripcion, precio, talla y color"                     , "Productos",
"Guardar producto y verificar en inventario"           ),
    ("RF-02", "Manejar variaciones de talla y color con existencias"                 , "Productos", "Registrar mismo producto con otra talla o color"),
    ("RF-03", "Agregar productos y actualizar cantidades de inventario"                  , "Productos", "Modificar stock y revisar movimiento"),
    ("RF-04", "Actualizar inventario automaticamente al registrar venta"                  , "Ventas", "Vender producto y comprobar disminucion"),
    ("RF-05", "Registrar movimientos de inventario"             , "Inventario", "Consultar movimientos de entrada, salida, ajuste, devolucion y cancelacion"),
    ("RF-06", "Registrar ventas con productos, cantidades y metodo de pago"                   , "Ventas", "Registrar venta con carrito"),
    ("RF-07", "Registrar pagos en efectivo, tarjeta y transferencia"                 , "Ventas", "Seleccionar metodo de pago"),
    ("RF-08", "Aplicar descuentos a ventas"          , "Ventas", "Capturar descuento general"           ),
    ("RF-09", "Registrar promociones con porcentaje y duracion"                , "Promociones", "Crear promocion vigente"),
    ("RF-10", "Aplicar descuentos automaticos segun condiciones"                , "Promociones y Ventas", "Venta aplica promocion vigente"),
    ("RF-11", "Registrar clientes con nombre, direccion, correo y telefono"                   , "Clientes", "Guardar cliente"),
    ("RF-12", "Almacenar y consultar historial de compras de cada cliente"                   , "Clientes y Reportes",
"Consultar historial"),
    ("RF-13", "Registrar proveedores e informacion de contacto"                , "Proveedores", "Guardar proveedor"),
    ("RF-14", "Relacionar proveedor con productos que suministra"                , "Productos y Proveedores",
"Consultar productos por proveedor"),
    ("RF-15", "Consultar productos disponibles e inventario por categoria"                   , "Reportes", "Reporte por categoria"),
    ("RF-16", "Consultar productos en oferta y descuentos"               , "Reportes", "Reporte de productos en oferta"),
    ("RF-17", "Consultar metodos de pago mas utilizados"              , "Reportes", "Reporte de metodos de pago"),
    ("RF-18", "Consultar productos mas vendidos en el ultimo mes"                , "Reportes", "Reporte mensual"),
    ("RF-19", "Consultar ventas realizadas en los ultimos tres dias"                 , "Reportes", "Reporte de ultimos tres dias"),
    ("RF-20", "Consultar productos de un proveedor especifico"                , "Reportes", "Parametro de proveedor"),
    ("RF-21", "Consultar productos comprados mas de una vez por un cliente"                   , "Reportes", "Parametro de cliente"),
    ("RF-22", "Consultar productos vendidos por categoria en el ultimo mes"                   , "Reportes", "Parametro de categoria"),
    ("RF-23", "Consultar productos con precio superior a cierto valor y existencias"                     , "Reportes",
"Parametro de precio"),
    ("RF-24", "Consultar producto con mayor descuento vigente"                , "Reportes", "Promociones vigentes"         ),
    ("RF-25", "Consultar compras por ciudad o region del cliente"                , "Reportes", "Agrupar por region"),
    ("RF-26", "Consultar productos no vendidos en los ultimos tres meses"                  , "Reportes", "Reporte sin ventas recientes"),
    ("RNF-01", "Reflejar en tiempo real la disminucion del inventario", "Ventas e Inventario",
"Validar stock inmediatamente despues de vender"            ),
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
        self.selected_customer_id = None
        self.selected_supplier_id = None
        self.selected_employee_id = None
        self.selected_promotion_id = None
        self.cart = []
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
        self.make_sales_tab(nb)
        self.make_customers_tab(nb)
        self.make_suppliers_tab(nb)
        self.make_employees_tab(nb)
        self.make_promotions_tab(nb)
        self.make_returns_tab(nb)
        self.make_reports_tab(nb)
        self.make_traceability_tab(nb)

    def clear_window(self):
        for child in self.winfo_children():
            child.destroy()
        self.productos_ui = None

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

    def make_sales_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Ventas")
        form = ttk.LabelFrame(tab, text="Nueva venta", padding=10)
        form.pack(fill="x")
        self.sale_customer_id = self.add_labeled_entry(form, "ID cliente", 0, 0)
        ttk.Label(form, text=f"Empleado: {self.user['name']} (ID {self.user['id']})").grid(row=0,
column=2, columnspan=2, sticky="w")
        ttk.Label(form, text="Metodo de pago").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        self.sale_payment = ttk.Combobox(form, values=PAYMENT_METHODS, state="readonly", width=24)
        self.sale_payment.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        self.sale_payment.set(PAYMENT_METHODS[0])
        self.sale_discount = self.add_labeled_entry(form, "Descuento venta %", 1, 2, default="0")
        self.sale_product_code = self.add_labeled_entry(form, "Codigo producto", 2, 0)
        self.sale_quantity = self.add_labeled_entry(form, "Cantidad", 2, 2, default="1")
        ttk.Button(form, text="Agregar al carrito"            , command=self.add_cart_item).grid(row=3,
column=0, pady=8)
        ttk.Button(form, text="Registrar venta", command=self.register_sale_ui).grid(row=3,
column=1, pady=8)
        ttk.Button(form, text="Vaciar carrito", command=self.clear_cart).grid(row=3, column=2,
pady=8)
        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, pady=8)
        cart_frame = ttk.LabelFrame(body, text="Carrito", padding=5)
        cart_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.cart_tree = self.make_tree(cart_frame, ("id", "codigo", "producto", "cantidad",
"precio", "promo", "subtotal"), height=14)
        ticket_frame = ttk.LabelFrame(body, text="Ticket", padding=5)
        ticket_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.ticket_text = tk.Text(ticket_frame, height=16, wrap="word")
        self.ticket_text.pack(fill="both", expand=True)

    def add_cart_item(self):
        try:
            code = self.sale_product_code.get().strip()
            qty = int(self.sale_quantity.get() or 1)
            product = self.db.one("SELECT * FROM products WHERE code=?", (code,))
            if not product:
                raise ValueError("No existe producto con ese codigo."                 )
            if qty <= 0:
                raise ValueError("Cantidad no valida.")
            current = sum(int(item["quantity"]) for item in self.cart if int(item["product_id"]) == int(product["id"]))
            if current + qty > int(product["stock"]):
                raise ValueError("Stock insuficiente.")
            for item in self.cart:
                if int(item["product_id"]) == int(product["id"]):
                    item["quantity"] += qty
                    break
            else:
                self.cart.append({"product_id": product["id"], "quantity": qty})
            self.sale_product_code.delete(0, tk.END)
            self.sale_quantity.delete(0, tk.END)
            self.sale_quantity.insert(0, "1")
            self.refresh_cart()
        except Exception as e:
            messagebox.showerror("Carrito", str(e))

    def refresh_cart(self):
        self.tree_clear(self.cart_tree)
        subtotal = 0.0
        for item in self.cart:
            product = self.db.one("SELECT * FROM products WHERE id=?", (item["product_id"],))
            if not product:
                continue
            promo = self.db.active_promotion_percent(product["id"])
            line = float(product["sale_price"]) * int(item["quantity"]) * (1 - promo / 100)
            subtotal += line
            self.cart_tree.insert("", tk.END, values=(product["id"], product["code"],
product["name"], item["quantity"], money(product["sale_price"]), f"{promo:g}%", money(line)))
        try:
            discount = float(self.sale_discount.get() or 0)
        except Exception:
            discount = 0
        total = subtotal * (1 - discount / 100)
        self.ticket_text.delete("1.0", tk.END)
        self.ticket_text.insert(tk.END, f"Subtotal con promociones: {money(subtotal)}\n")
        self.ticket_text.insert(tk.END, f"Descuento general: {discount:g}%\n")
        self.ticket_text.insert(tk.END, f"Total estimado: {money(total)}\n")

    def register_sale_ui(self):
        try:
            customer = self.sale_customer_id.get().strip()
            customer_id = int(customer) if customer else None
            sale_id, subtotal, discount_amount, total = self.db.register_sale(customer_id,
int(self.user["id"]), self.sale_payment.get(), float(self.sale_discount.get() or 0), self.cart)
            self.ticket_text.delete("1.0", tk.END)
            self.ticket_text.insert(tk.END, f"VENTA REGISTRADA\nTicket: {sale_id}\nFecha: {now_text()}\nSubtotal: {money(subtotal)}\nDescuento: {money(discount_amount)}\nTotal: {money(total)}\nMetodo: {self.sale_payment.get()}\n")
            self.clear_cart(True)
            self.refresh_products()
            messagebox.showinfo("Venta", f"Venta registrada con ticket                  {sale_id}.")
        except Exception as e:
            messagebox.showerror("Venta", str(e))

    def clear_cart(self, keep_ticket=False):
        self.cart = []
        self.tree_clear(self.cart_tree)
        if not keep_ticket:
            self.ticket_text.delete("1.0", tk.END)

    def make_customers_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Clientes")
        form = ttk.LabelFrame(tab, text="Cliente", padding=10)
        form.pack(fill="x")
        self.c_name = self.add_labeled_entry(form, "Nombre", 0, 0)
        self.c_phone = self.add_labeled_entry(form, "Telefono", 0, 2)
        self.c_email = self.add_labeled_entry(form, "Correo", 1, 0)
        self.c_address = self.add_labeled_entry(form, "Direccion", 1, 2)
        self.c_region = self.add_labeled_entry(form, "Ciudad/region", 2, 0)
        self.c_preferences = self.add_labeled_entry(form, "Preferencias", 2, 2)
        ttk.Button(form, text="Guardar cliente", command=self.save_customer_ui).grid(row=3,
column=0, pady=8)
        ttk.Button(form, text="Limpiar", command=self.clear_customer_form                  ).grid(row=3, column=1,
pady=8)
        ttk.Button(form, text="Ver historial", command=self.show_customer_history).grid(row=3,
column=2, pady=8)
        ttk.Button(form, text="Correo profesional"            , command=self.show_customer_email).grid(row=3,
column=3, pady=8)
        table = ttk.LabelFrame(tab, text="Clientes registrados", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.customers_tree = self.make_tree(table, ("id", "nombre", "telefono", "correo", "region",
"preferencias"), height=16)
        self.customers_tree.bind("<<TreeviewSelect>>", self.load_customer_selected)
        self.refresh_customers       ()

    def save_customer_ui(self):
        try:
            if not self.c_name.get().strip():
                raise ValueError("El nombre es obligatorio.")
            data = (self.c_name.get().strip(), self.c_phone.get().strip(),
self.c_email.get().strip(), self.c_address.get().strip(), self.c_region.get().strip(),
self.c_preferences.get().strip())
            self.selected_customer_id = self.db.save_customer(self.selected_customer_id, data)
            self.refresh_customers()
            messagebox.showinfo("Clientes", "Cliente guardado.")
        except Exception as e:
            messagebox.showerror("Clientes", str(e))

    def refresh_customers(self):
        rows = self.db.query("SELECT id, name AS nombre, phone AS telefono, email AS correo, city_region AS region, preferences AS preferencias FROM customers ORDER BY id DESC"                     )
        self.tree_clear(self.customers_tree)
        for row in rows:
            self.customers_tree.insert("", tk.END, values=[row[key] for key in row.keys()])

    def load_customer_selected(self, event=None):
        sel = self.customers_tree.selection()
        if not sel:
            return
        customer_id = self.customers_tree.item(sel[0], "values")[0]
        row = self.db.one("SELECT * FROM customers WHERE id=?", (customer_id,))
        if not row:
            return
        self.selected_customer_id = row["id"]
        self.set_entries([self.c_name, self.c_phone, self.c_email, self.c_address, self.c_region,
self.c_preferences], [row["name"], row["phone"], row["email"], row["address"], row["city_region"],
row["preferences"]])

    def clear_customer_form(self):
        self.selected_customer_id = None
        for entry in [self.c_name, self.c_phone, self.c_email, self.c_address, self.c_region,
self.c_preferences]:
            entry.delete(0, tk.END)

    def show_customer_history(self):
        try:
            if not self.selected_customer_id:
                raise ValueError("Selecciona un cliente.")
            rows = self.db.customer_history(self.selected_customer_id)
            win = tk.Toplevel(self)
            win.title("Historial de cliente")
            text = tk.Text(win, width=105, height=28)
            text.pack(fill="both", expand=True, padx=10, pady=10)
            if not rows:
                text.insert(tk.END, "Sin compras registradas.")
            for row in rows:
                text.insert(tk.END, f"Venta {row['venta']} | {row['fecha']} | {row['codigo']} {row['producto']} | Cantidad {row['cantidad']} | Linea {money(row['total_linea'])} | Total venta {money(row['total_venta'])} | {row['estado']}\n")
        except Exception as e:
            messagebox.showerror("Historial", str(e))

    def build_customer_email_content(self, customer_id):
        customer = self.db.one("SELECT * FROM customers WHERE id=?", (customer_id,))
        if not customer:
            raise ValueError("Cliente no encontrado.")
        stats = self.db.one("SELECT COUNT(*) AS compras, COALESCE(SUM(total),0) AS total, MAX(sale_datetime) AS ultima FROM sales WHERE customer_id=? AND status='ACTIVA'", (customer_id,))
        favorite = self.db.one("""SELECT p.name AS producto, SUM(si.quantity) AS piezas FROM sales s
JOIN sale_items si ON si.sale_id=s.id JOIN products p ON p.id=si.product_id WHERE s.customer_id=?
AND s.status='ACTIVA' GROUP BY p.id ORDER BY piezas DESC LIMIT 1""", (customer_id,))
        name = customer["name"] or "cliente"
        first_name = name.split()[0] if name.split() else name
        preferences = customer["preferences"] or ""
        compras = int(stats["compras"] or 0) if stats else 0
        total = float(stats["total"] or 0) if stats else 0
        ultima = stats["ultima"] if stats else ""
        subject = "Gracias por su preferencia en Mis trapitos"
        lines = []
        lines.append(f"Estimado/a {first_name}:")
        lines.append("")
        lines.append("Esperamos que se encuentre muy bien. En Mis trapitos queremos agradecerle sinceramente su preferencia y la confianza que ha depositado en nuestra tienda.")
        if compras > 0:
            lines.append(f"De acuerdo con su historial, contamos con {compras} compra(s) registrada(s) a su nombre, por un total acumulado de {money(total)}.")
            if ultima:
                lines.append(f"Su compra mas reciente fue registrada el                   {ultima}.")
        if favorite:
            lines.append(f"Tambien identificamos que uno de los productos que mas ha adquirido es: {favorite['producto']}.")
        if preferences:
            lines.append(f"Tomaremos en cuenta sus preferencias registradas: {preferences}.")
        lines.append("Queremos invitarle a visitarnos nuevamente para conocer nuestras prendas disponibles, promociones vigentes y nuevas opciones de temporada."                )
        lines.append("Si desea consultar disponibilidad, tallas, colores o recibir atencion personalizada, con gusto podemos apoyarle por este mismo medio."                )
        lines.append("")
        lines.append("Quedamos atentos a cualquier duda o solicitud.")
        lines.append("")
        lines.append("Atentamente,")
        lines.append("Mis trapitos")
        lines.append("Tienda de ropa")
        return customer, subject, "\n".join(lines)

    def show_customer_email(self):
        try:
            if not self.selected_customer_id:
                raise ValueError("Selecciona un cliente.")
            customer, subject, body = self.build_customer_email_content(self.selected_customer_id)
            win = tk.Toplevel(self)
            win.title("Correo profesional para cliente")
            win.geometry("820x560")
            frame = ttk.Frame(win, padding=10)
            frame.pack(fill="both", expand=True)
            ttk.Label(frame, text=f"Para: {customer['email'] or 'Sin correo registrado'}",
font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
            ttk.Label(frame, text="Asunto").pack(anchor="w")
            subject_entry = ttk.Entry(frame)
            subject_entry.pack(fill="x", pady=(0, 8))
            subject_entry.insert(0, subject)
            ttk.Label(frame, text="Mensaje").pack(anchor="w")
            text = tk.Text(frame, height=22, wrap="word")
            text.pack(fill="both", expand=True)
            text.insert(tk.END, body)
            buttons = ttk.Frame(frame)
            buttons.pack(fill="x", pady=8)

            def copy_email():
                content = f"Asunto: {subject_entry.get().strip()}\n\n{text.get('1.0', tk.END).strip()}"
                self.clipboard_clear()
                self.clipboard_append(content)
                messagebox.showinfo("Correo", "Correo copiado al portapapeles."                   )

            def open_email_client():
                email = customer["email"] or ""
                if not email.strip():
                    raise ValueError("El cliente no tiene correo registrado.")
                mailto = "mailto:" + urllib.parse.quote(email.strip()) + "?subject=" + urllib.parse.quote(subject_entry.get().strip()) + "&body=" + urllib.parse.quote(text.get("1.0",
tk.END).strip())
                webbrowser.open(mailto)

            def open_email_client_safe():
                try:
                    open_email_client()
                except Exception as e:
                    messagebox.showerror("Correo", str(e))

            ttk.Button(buttons, text="Copiar correo", command=copy_email).pack(side="left", padx=4)
            ttk.Button(buttons, text="Abrir en correo",
command=open_email_client_safe).pack(side="left", padx=4)
            ttk.Button(buttons, text="Cerrar", command=win.destroy).pack(side="right", padx=4)
        except Exception as e:
            messagebox.showerror("Correo", str(e))

    def make_suppliers_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Proveedores")
        form = ttk.LabelFrame(tab, text="Proveedor", padding=10)
        form.pack(fill="x")
        self.s_name = self.add_labeled_entry(form, "Nombre", 0, 0)
        self.s_phone = self.add_labeled_entry(form, "Telefono", 0, 2)
        self.s_address = self.add_labeled_entry(form, "Direccion", 1, 0)
        self.s_products = self.add_labeled_entry(form, "Productos suministrados"                    , 1, 2)
        self.s_last_order = self.add_labeled_entry(form, "Ultimo pedido", 2, 0,
default=today_text())
        ttk.Button(form, text="Guardar proveedor", command=self.save_supplier_ui).grid(row=3,
column=0, pady=8)
        ttk.Button(form, text="Limpiar", command=self.clear_supplier_form                  ).grid(row=3, column=1,
pady=8)
        table = ttk.LabelFrame(tab, text="Proveedores registrados", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.suppliers_tree = self.make_tree(table, ("id", "nombre", "telefono", "direccion",
"suministra", "ultimo_pedido"), height=16)
        self.suppliers_tree.bind("<<TreeviewSelect>>"             , self.load_supplier_selected)
        self.refresh_suppliers       ()

    def save_supplier_ui(self):
        try:
            if not self.s_name.get().strip():
                raise ValueError("El nombre es obligatorio.")
            data = (self.s_name.get().strip(), self.s_phone.get().strip(),
self.s_address.get().strip(), self.s_products.get().strip(), self.s_last_order.get().strip() or
today_text())
            self.selected_supplier_id = self.db.save_supplier(self.selected_supplier_id, data)
            self.refresh_suppliers()
            messagebox.showinfo("Proveedores", "Proveedor guardado.")
        except Exception as e:
            messagebox.showerror("Proveedores", str(e))

    def refresh_suppliers(self):
        rows = self.db.query("SELECT id, name AS nombre, phone AS telefono, address AS direccion, products_supplied AS suministra, last_order_date AS ultimo_pedido FROM suppliers ORDER BY id DESC"                        )
        self.tree_clear(self.suppliers_tree)
        for row in rows:
            self.suppliers_tree.insert("", tk.END, values=[row[key] for key in row.keys()])

    def load_supplier_selected(self, event=None):
        sel = self.suppliers_tree.selection()
        if not sel:
            return
        supplier_id = self.suppliers_tree.item(sel[0], "values")[0]
        row = self.db.one("SELECT * FROM suppliers WHERE id=?", (supplier_id,))
        if not row:
            return
        self.selected_supplier_id = row["id"]
        self.set_entries([self.s_name, self.s_phone, self.s_address, self.s_products,
self.s_last_order], [row["name"], row["phone"], row["address"], row["products_supplied"],
row["last_order_date"]])

    def clear_supplier_form(self):
        self.selected_supplier_id = None
        for entry in [self.s_name, self.s_phone, self.s_address, self.s_products,
self.s_last_order]:
            entry.delete(0, tk.END)
        self.s_last_order.insert(0, today_text())

    def make_employees_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Empleados")
        form = ttk.LabelFrame(tab, text="Empleado", padding=10)
        form.pack(fill="x")
        self.e_name = self.add_labeled_entry(form, "Nombre", 0, 0)
        self.e_username = self.add_labeled_entry(form, "Usuario", 0, 2)
        self.e_password = self.add_labeled_entry(form, "Contraseña", 1, 0)
        self.e_role = self.add_labeled_entry(form, "Rol", 1, 2)
        ttk.Button(form, text="Guardar empleado", command=self.save_employee_ui).grid(row=2,
column=0, pady=8)
        ttk.Button(form, text="Limpiar", command=self.clear_employee_form                  ).grid(row=2, column=1,
pady=8)
        table = ttk.LabelFrame(tab, text="Empleados registrados", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.employees_tree = self.make_tree(table, ("id", "nombre", "usuario", "rol"), height=16)
        self.employees_tree.bind("<<TreeviewSelect>>", self.load_employee_selected)
        self.refresh_employees       ()

    def save_employee_ui(self):
        try:
            if not self.e_name.get().strip() or not self.e_username.get().strip():
                raise ValueError("Nombre y usuario son obligatorios.")
            self.selected_employee_id = self.db.save_employee(self.selected_employee_id,
self.e_name.get().strip(), self.e_username.get().strip(), self.e_password.get().strip(),
self.e_role.get().strip() or "Ventas")
            self.refresh_employees()
            messagebox.showinfo("Empleados", "Empleado guardado.")
        except Exception as e:
            messagebox.showerror("Empleados", str(e))

    def refresh_employees(self):
        rows = self.db.query("SELECT id, name AS nombre, username AS usuario, role AS rol FROM employees ORDER BY id DESC")
        self.tree_clear(self.employees_tree)
        for row in rows:
            self.employees_tree.insert("", tk.END, values=[row[key] for key in row.keys()])

    def load_employee_selected(self, event=None):
        sel = self.employees_tree.selection()
        if not sel:
            return
        employee_id = self.employees_tree.item(sel[0], "values")[0]
        row = self.db.one("SELECT * FROM employees WHERE id=?", (employee_id,))
        if not row:
            return
        self.selected_employee_id = row["id"]
        self.set_entries([self.e_name, self.e_username, self.e_password, self.e_role], [row["name"],
row["username"], "", row["role"]])

    def clear_employee_form(self):
        self.selected_employee_id = None
        for entry in [self.e_name, self.e_username, self.e_password, self.e_role]:
            entry.delete(0, tk.END)

    def make_promotions_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Promociones")
        form = ttk.LabelFrame(tab, text="Promocion", padding=10)
        form.pack(fill="x")
        self.pr_product = self.add_labeled_entry(form, "ID producto", 0, 0)
        self.pr_discount = self.add_labeled_entry(form, "Descuento %", 0, 2)
        self.pr_start = self.add_labeled_entry(form, "Inicio", 1, 0, default=today_text())
        self.pr_end = self.add_labeled_entry(form, "Fin", 1, 2, default=date_offset(30))
        ttk.Button(form, text="Guardar promocion", command=self.save_promotion_ui).grid(row=2,
column=0, pady=8)
        ttk.Button(form, text="Limpiar", command=self.clear_promotion_form).grid(row=2, column=1,
pady=8)
        table = ttk.LabelFrame(tab, text="Promociones registradas", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.promotions_tree = self.make_tree(table, ("id", "producto_id", "codigo", "producto",
"descuento", "inicio", "fin"), height=16)
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
            self.selected_promotion_id = self.db.save_promotion(self.selected_promotion_id,
product_id, discount, self.pr_start.get().strip() or today_text(), self.pr_end.get().strip() or
today_text())
            self.refresh_promotions()
            messagebox.showinfo("Promociones", "Promocion guardada.")
        except Exception as e:
            messagebox.showerror("Promociones", str(e))

    def refresh_promotions(self):
        rows = self.db.query("""SELECT pr.id, pr.product_id AS producto_id, p.code AS codigo, p.name
AS producto, pr.discount_percent AS descuento, pr.start_date AS inicio, pr.end_date AS fin FROM
promotions pr JOIN products p ON p.id=pr.product_id ORDER BY pr.id DESC"""                  )
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
        self.set_entries([self.pr_product, self.pr_discount, self.pr_start, self.pr_end],
[row["product_id"], row["discount_percent"], row["start_date"], row["end_date"]])

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
        ttk.Button(form, text="Registrar devolucion", command=self.return_item_ui).grid(row=2,
column=0, pady=8)
        self.cancel_sale_entry = self.add_labeled_entry(form, "Venta a cancelar"                    , 3, 0)
        self.cancel_reason = self.add_labeled_entry(form, "Motivo cancelacion", 3, 2)
        ttk.Button(form, text="Cancelar venta", command=self.cancel_sale_ui).grid(row=4, column=0,
pady=8)
        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, pady=8)
        returns_frame = ttk.LabelFrame(body, text="Devoluciones", padding=5)
        returns_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.returns_tree = self.make_tree(returns_frame, ("id", "venta", "producto", "cantidad",
"fecha", "motivo"), height=14)
        cancellations_frame = ttk.LabelFrame(body, text="Cancelaciones", padding=5)
        cancellations_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.cancellations_tree = self.make_tree(cancellations_frame, ("id", "venta", "fecha",
"motivo"), height=14)
        self.refresh_returns()

    def return_item_ui(self):
        try:
            self.db.return_item(int(self.r_sale.get()), int(self.r_product.get()),
int(self.r_quantity.get()), self.r_reason.get().strip())
            self.refresh_returns()
            self.refresh_products()
            messagebox.showinfo("Devolucion", "Devolucion registrada."                 )
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
p.id=r.product_id ORDER BY r.id DESC"""         )
        self.tree_clear(self.returns_tree)
        for row in rows:
            self.returns_tree.insert("", tk.END, values=[row[key] for key in row.keys()])
        rows = self.db.query("SELECT id, sale_id AS venta, cancel_datetime AS fecha, reason AS motivo FROM cancellations ORDER BY id DESC"          )
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
        self.report_param = self.add_labeled_entry            (controls, "Parametro", 0, 2, width=30)
        ttk.Button(controls, text="Ejecutar", command=self.run_report).grid(row=0, column=4, padx=4,
pady=4)
        ttk.Button(controls, text="Exportar CSV", command=self.export_report_csv).grid(row=0,
column=5, padx=4, pady=4)
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
        ttk.Button(tab, text="Ejecutar pruebas basicas",
command=self.run_basic_tests).pack(anchor="w", pady=5)

    def run_basic_tests(self):
        try:
            product = self.db.one("SELECT * FROM products ORDER BY stock DESC LIMIT 1")
            employee = self.db.one("SELECT * FROM employees ORDER BY id LIMIT 1")
            customer = self.db.one("SELECT * FROM customers ORDER BY id LIMIT 1")
            if not product or not employee:
                raise ValueError("Faltan productos o empleados para probar.")
            initial_stock = int(product["stock"])
            if initial_stock < 1:
                raise ValueError("No hay stock suficiente para la prueba."                  )
            sale_id, subtotal, discount_amount, total = self.db.register_sale(customer["id"] if
customer else None, employee["id"], PAYMENT_METHODS[0], 0, [{"product_id": product["id"],
"quantity": 1}])
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

