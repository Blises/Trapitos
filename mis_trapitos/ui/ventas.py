import tkinter as tk
from tkinter import messagebox, ttk
from typing import NamedTuple

from mis_trapitos.data.database import PAYMENT_METHODS

def money(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"


class ResultadoVenta(NamedTuple):
    sale_id: int
    fecha: str
    subtotal: float
    descuento: float
    total: float
    metodo_pago: str


class ServicioVentas:
    def __init__(self, db):
        self.db = db

        self.cart = []

    # ------------------------------------------------------------------ carrito
    def cantidad_en_carrito(self, product_id):
        return sum(int(i["quantity"]) for i in self.cart if int(i["product_id"]) == int(product_id))

    def agregar_producto(self, code, quantity=1):
        """Agrega al carrito validando existencia, cantidad y stock disponible."""
        code = (code or "").strip()
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Cantidad no valida.")
        product = self.db.one("SELECT * FROM products WHERE code=?", (code,))
        if not product:
            raise ValueError("No existe producto con ese codigo.")
        if qty <= 0:
            raise ValueError("Cantidad no valida.")
        if self.cantidad_en_carrito(product["id"]) + qty > int(product["stock"]):
            raise ValueError("Stock insuficiente.")
        for item in self.cart:
            if int(item["product_id"]) == int(product["id"]):
                item["quantity"] += qty
                break
        else:
            self.cart.append({"product_id": product["id"], "quantity": qty})

    def vaciar(self):
        self.cart = []

    def lineas(self):
        """Devuelve las partidas del carrito con promoción vigente y total de línea."""
        rows = []
        for item in self.cart:
            product = self.db.one("SELECT * FROM products WHERE id=?", (item["product_id"],))
            if not product:
                continue
            promo = self.db.active_promotion_percent(product["id"])
            qty = int(item["quantity"])
            line = float(product["sale_price"]) * qty * (1 - promo / 100)
            rows.append({
                "id": product["id"], "code": product["code"], "name": product["name"],
                "quantity": qty, "unit_price": float(product["sale_price"]),
                "promo": promo, "line_total": line,
            })
        return rows

    # ------------------------------------------------------------------ totales
    @staticmethod
    def parsear_descuento(valor):
        try:
            descuento = float(valor or 0)
        except (TypeError, ValueError):
            raise ValueError("El descuento debe ser un numero.")
        if descuento < 0 or descuento > 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")
        return descuento

    def totales(self, descuento=0):
        """Regresa (subtotal con promociones, monto de descuento, total)."""
        descuento = self.parsear_descuento(descuento)
        subtotal = sum(line["line_total"] for line in self.lineas())
        monto = subtotal * descuento / 100
        return subtotal, monto, subtotal - monto

    # -------------------------------------------------------------------- venta
    def registrar_venta(self, customer_id, employee_id, metodo_pago, descuento=0):
        """Registra la venta del carrito y deja el inventario actualizado.

        Si algo falla, Database.register_sale revierte la transacción completa y
        el carrito se conserva para que el usuario pueda corregir y reintentar.
        El carrito solo se vacía cuando la venta quedó guardada.
        """
        if not self.cart:
            raise ValueError("La venta no tiene productos.")
        if metodo_pago not in PAYMENT_METHODS:
            raise ValueError("Metodo de pago no valido.")
        descuento = self.parsear_descuento(descuento)
        if customer_id is not None and not self.db.one("SELECT id FROM customers WHERE id=?", (customer_id,)):
            raise ValueError("Cliente no encontrado.")
        sale_id, subtotal, monto, total = self.db.register_sale(
            customer_id, employee_id, metodo_pago, descuento, self.cart
        )
        fecha = self.db.scalar("SELECT sale_datetime FROM sales WHERE id=?", (sale_id,))
        self.vaciar()
        return ResultadoVenta(sale_id, fecha, subtotal, monto, total, metodo_pago)


class VentasUI(ttk.Frame):
    """Pestaña de ventas. `on_venta_registrada` se invoca tras guardar una venta
    para que otras pestañas (p. ej. Productos) refresquen su inventario."""

    def __init__(self, parent, db, user, on_venta_registrada=None):
        super().__init__(parent, padding=10)
        self.db = db
        self.user = user
        self.on_venta_registrada = on_venta_registrada
        self.servicio = ServicioVentas(db)
        self._build_widgets()

    @staticmethod
    def _add_labeled_entry(parent, text, row, column, width=26, default=""):
        parent.columnconfigure(column + 1, weight=1)
        ttk.Label(parent, text=text).grid(row=row, column=column, sticky="e", padx=(4, 8), pady=5)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 10), pady=5)
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
        preferred_widths = {
            "id": 58, "codigo": 110, "producto": 190, "producto_id": 85,
            "categoria": 125, "talla": 75, "color": 100, "stock": 75,
            "precio": 105, "proveedor": 145, "nombre": 175, "telefono": 120,
            "correo": 190, "region": 135, "preferencias": 180, "direccion": 210,
            "suministra": 190, "ultimo_pedido": 120, "usuario": 130, "rol": 125,
            "descuento": 100, "inicio": 105, "fin": 105, "cantidad": 90,
            "fecha": 145, "motivo": 210, "venta": 75, "metodo": 165,
            "total": 110, "periodo": 130, "piezas": 90, "ventas": 110,
            "empleado": 170, "costo": 110, "utilidad": 110, "tipo": 125,
            "codigo": 120, "requerimiento": 420, "modulo": 170, "prueba": 300,
            "elemento": 220, "valor": 260, "estado": 125, "resultado": 220,
            "mensaje": 520,
        }
        for col in columns:
            tree.heading(col, text=col)
            width = preferred_widths.get(col, 130)
            tree.column(col, width=width, minwidth=max(55, min(width, 90)), anchor="w", stretch=True)
        return tree


    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="Nueva venta", padding=10)
        form.pack(fill="x")
        self.sale_customer_id = self._add_labeled_entry(form, "ID cliente", 0, 0)
        ttk.Label(
            form, text=f"Empleado: {self.user['name']} (ID {self.user['id']})"
        ).grid(row=0, column=2, columnspan=2, sticky="w")
        ttk.Label(form, text="Metodo de pago").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        self.sale_payment = ttk.Combobox(form, values=PAYMENT_METHODS, state="readonly", width=24)
        self.sale_payment.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        self.sale_payment.set(PAYMENT_METHODS[0])
        self.sale_discount = self._add_labeled_entry(form, "Descuento venta %", 1, 2, default="0")
        self.sale_product_code = self._add_labeled_entry(form, "Codigo producto", 2, 0)
        self.sale_quantity = self._add_labeled_entry(form, "Cantidad", 2, 2, default="1")
        ttk.Button(form, text="Agregar al carrito", style="Accent.TButton", command=self.add_cart_item).grid(row=3, column=0, pady=8)
        ttk.Button(form, text="Registrar venta", style="Accent.TButton", command=self.register_sale_ui).grid(row=3, column=1, pady=8)
        ttk.Button(form, text="Vaciar carrito", style="Danger.TButton", command=self.clear_cart).grid(row=3, column=2, pady=8)
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)
        cart_frame = ttk.LabelFrame(body, text="Carrito", padding=5)
        cart_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.cart_tree = self._make_tree(
            cart_frame, ("id", "codigo", "producto", "cantidad", "precio", "promo", "subtotal"), height=14
        )
        ticket_frame = ttk.LabelFrame(body, text="Ticket", padding=5)
        ticket_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.ticket_text = tk.Text(
            ticket_frame, height=16, wrap="word", bg="#FFFFFF", fg="#1F2937",
            insertbackground="#24456B", relief="solid", borderwidth=1,
            highlightthickness=1, highlightbackground="#D6DEE8",
            highlightcolor="#2A9D8F", padx=12, pady=10, font=("Segoe UI", 10),
        )
        self.ticket_text.pack(fill="both", expand=True)

    def add_cart_item(self):
        try:
            self.servicio.agregar_producto(self.sale_product_code.get(), self.sale_quantity.get() or 1)
            self.sale_product_code.delete(0, tk.END)
            self.sale_quantity.delete(0, tk.END)
            self.sale_quantity.insert(0, "1")
            self.refresh_cart()
        except Exception as e:
            messagebox.showerror("Carrito", str(e))

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        for line in self.servicio.lineas():
            self.cart_tree.insert("", tk.END, values=(
                line["id"], line["code"], line["name"], line["quantity"],
                money(line["unit_price"]), f"{line['promo']:g}%", money(line["line_total"]),
            ))
        try:
            subtotal, _, total = self.servicio.totales(self.sale_discount.get())
            discount = float(self.sale_discount.get() or 0)
        except ValueError:
            subtotal, _, total = self.servicio.totales(0)
            discount = 0
        self.ticket_text.delete("1.0", tk.END)
        self.ticket_text.insert(tk.END, f"Subtotal con promociones: {money(subtotal)}\n")
        self.ticket_text.insert(tk.END, f"Descuento general: {discount:g}%\n")
        self.ticket_text.insert(tk.END, f"Total estimado: {money(total)}\n")

    def register_sale_ui(self):
        try:
            customer = self.sale_customer_id.get().strip()
            customer_id = int(customer) if customer else None
            r = self.servicio.registrar_venta(
                customer_id, int(self.user["id"]), self.sale_payment.get(), self.sale_discount.get()
            )
            self.ticket_text.delete("1.0", tk.END)
            self.ticket_text.insert(
                tk.END,
                f"VENTA REGISTRADA\nTicket: {r.sale_id}\nFecha: {r.fecha}\n"
                f"Subtotal: {money(r.subtotal)}\nDescuento: {money(r.descuento)}\n"
                f"Total: {money(r.total)}\nMetodo: {r.metodo_pago}\n",
            )
            self.clear_cart(keep_ticket=True)
            if self.on_venta_registrada:
                self.on_venta_registrada()
            messagebox.showinfo("Venta", f"Venta registrada con ticket {r.sale_id}.")
        except Exception as e:
            messagebox.showerror("Venta", str(e))

    def clear_cart(self, keep_ticket=False):
        self.servicio.vaciar()
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        if not keep_ticket:
            self.ticket_text.delete("1.0", tk.END)
