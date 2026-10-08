import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from mis_trapitos.data.database import Database, DB_NAME, PAYMENT_METHODS
from mis_trapitos.ui.base import add_labeled_entry, make_tree
from mis_trapitos.ui.contactos import ContactosUI
from mis_trapitos.ui.devoluciones import DevolucionesUI
from mis_trapitos.ui.login import Login
from mis_trapitos.ui.productos import ProductosUI
from mis_trapitos.ui.promociones import PromocionesUI
from mis_trapitos.ui.ventas import VentasUI, ServicioVentas

APP_TITLE = "Mis trapitos - Sistema local"
APP_VERSION = "7.0"

UI_COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_alt": "#EEF3F8",
    "text": "#1F2937",
    "muted": "#64748B",
    "border": "#D6DEE8",
    "primary": "#24456B",
    "primary_active": "#193653",
    "accent": "#2A9D8F",
    "accent_active": "#217D72",
    "danger": "#B84A55",
    "danger_active": "#943A44",
    "selection": "#D9EAF7",
}

CONFIG_ITEMS = [
    ("CI-01", "Codigo fuente principal", "main.py", "Controlado"),
    ("CI-02", "Base de datos local", "mis_trapitos.db", "Controlado"),
    ("CI-03", "Version de aplicacion", APP_VERSION, "Controlado"),
    ("CI-04", "Operacion sin Internet", "SQLite local y Tkinter", "Controlado"),
    ("CI-05", "Usuario inicial", "admin / 1234", "Controlado"),
    ("CI-06", "Modulo de productos", "mis_trapitos/ui/productos.py", "Controlado"),
    ("CI-07", "Modulo de contactos y usuarios", "mis_trapitos/ui/contactos.py", "Controlado"),
    ("CI-08", "Modulo de ventas", "mis_trapitos/ui/ventas.py", "Controlado"),
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


class App(tk.Tk):
    def __init__(self, db_path=None):
        super().__init__()
        self._configure_styles()
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1360x840")
        self.minsize(1060, 680)
        self.configure(bg=UI_COLORS["background"])
        try:
            self.db = Database(DB_NAME if db_path is None else db_path)
        except Exception:
            self.destroy()
            raise
        self.user = None
        self.login_view = None
        self.productos_ui = None
        self.contactos_ui = None
        self.ventas_ui = None
        self.main_notebook = None
        self.navigation_buttons = []
        self.module_title = tk.StringVar(self, value="Productos")
        self.promociones_ui = None
        self.devoluciones_ui = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login()

    def _configure_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), foreground=UI_COLORS["text"])
        style.configure("TFrame", background=UI_COLORS["background"])
        style.configure("Surface.TFrame", background=UI_COLORS["surface"])
        style.configure("Header.TFrame", background=UI_COLORS["primary"])
        style.configure("Login.TFrame", background=UI_COLORS["background"])
        style.configure(
            "TLabel",
            background=UI_COLORS["background"],
            foreground=UI_COLORS["text"],
            padding=(2, 2),
        )
        style.configure(
            "Muted.TLabel",
            background=UI_COLORS["background"],
            foreground=UI_COLORS["muted"],
        )
        style.configure(
            "Card.TLabel",
            background=UI_COLORS["surface"],
            foreground=UI_COLORS["text"],
        )
        style.configure(
            "Brand.TLabel",
            background=UI_COLORS["background"],
            foreground=UI_COLORS["primary"],
            font=("Segoe UI", 25, "bold"),
        )
        style.configure(
            "Header.TLabel",
            background=UI_COLORS["primary"],
            foreground="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            padding=(4, 2),
        )
        style.configure(
            "HeaderMuted.TLabel",
            background=UI_COLORS["primary"],
            foreground="#DCE8F5",
            font=("Segoe UI", 9),
            padding=(4, 2),
        )
        style.configure("Sidebar.TFrame", background=UI_COLORS["primary"])
        style.configure("Workspace.TFrame", background=UI_COLORS["background"])
        style.configure("WorkspaceHeader.TFrame", background=UI_COLORS["surface"])
        style.configure(
            "SidebarBrand.TLabel",
            background=UI_COLORS["primary"],
            foreground="#FFFFFF",
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "SidebarMuted.TLabel",
            background=UI_COLORS["primary"],
            foreground="#AFC5D9",
            font=("Segoe UI", 9),
        )
        style.configure(
            "SidebarSection.TLabel",
            background=UI_COLORS["primary"],
            foreground="#AFC5D9",
            font=("Segoe UI", 8, "bold"),
        )
        style.configure(
            "Sidebar.TButton",
            background=UI_COLORS["primary"],
            foreground="#D8E6F2",
            bordercolor=UI_COLORS["primary"],
            lightcolor=UI_COLORS["primary"],
            darkcolor=UI_COLORS["primary"],
            relief="flat",
            anchor="w",
            padding=(14, 10),
            font=("Segoe UI", 10),
        )
        style.map(
            "Sidebar.TButton",
            background=[("active", "#315574"), ("pressed", "#315574")],
            foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")],
        )
        style.configure(
            "SidebarActive.TButton",
            background=UI_COLORS["accent"],
            foreground="#FFFFFF",
            bordercolor=UI_COLORS["accent"],
            lightcolor=UI_COLORS["accent"],
            darkcolor=UI_COLORS["accent"],
            relief="flat",
            anchor="w",
            padding=(14, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "SidebarActive.TButton",
            background=[("active", UI_COLORS["accent_active"]), ("pressed", UI_COLORS["accent_active"])],
        )
        style.configure(
            "SidebarLogout.TButton",
            background=UI_COLORS["primary"],
            foreground="#D8E6F2",
            bordercolor="#315574",
            lightcolor=UI_COLORS["primary"],
            darkcolor=UI_COLORS["primary"],
            relief="flat",
            anchor="w",
            padding=(0, 8),
            font=("Segoe UI", 9),
        )
        style.configure(
            "WorkspaceTitle.TLabel",
            background=UI_COLORS["surface"],
            foreground=UI_COLORS["text"],
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "WorkspaceMuted.TLabel",
            background=UI_COLORS["surface"],
            foreground=UI_COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure("Content.TFrame", background=UI_COLORS["background"])
        style.configure(
            "Hidden.TNotebook",
            background=UI_COLORS["background"],
            borderwidth=0,
            padding=0,
        )
        style.layout("Hidden.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        style.layout("Hidden.TNotebook.Tab", [])
        style.configure(
            "TLabelframe",
            background=UI_COLORS["background"],
            bordercolor=UI_COLORS["background"],
            relief="flat",
            borderwidth=0,
        )
        style.configure(
            "TLabelframe.Label",
            background=UI_COLORS["background"],
            foreground=UI_COLORS["primary"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TButton",
            background=UI_COLORS["primary"],
            foreground="#FFFFFF",
            bordercolor=UI_COLORS["primary"],
            lightcolor=UI_COLORS["primary"],
            darkcolor=UI_COLORS["primary"],
            padding=(12, 7),
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TButton",
            background=[("pressed", UI_COLORS["primary_active"]), ("active", UI_COLORS["primary_active"])],
            foreground=[("disabled", "#AAB5C2"), ("!disabled", "#FFFFFF")],
        )
        style.configure(
            "Accent.TButton",
            background=UI_COLORS["accent"],
            bordercolor=UI_COLORS["accent"],
            lightcolor=UI_COLORS["accent"],
            darkcolor=UI_COLORS["accent"],
        )
        style.map(
            "Accent.TButton",
            background=[("pressed", UI_COLORS["accent_active"]), ("active", UI_COLORS["accent_active"])],
        )
        style.configure(
            "Danger.TButton",
            background=UI_COLORS["danger"],
            bordercolor=UI_COLORS["danger"],
            lightcolor=UI_COLORS["danger"],
            darkcolor=UI_COLORS["danger"],
        )
        style.map(
            "Danger.TButton",
            background=[("pressed", UI_COLORS["danger_active"]), ("active", UI_COLORS["danger_active"])],
        )
        style.configure(
            "TEntry",
            fieldbackground=UI_COLORS["surface"],
            foreground=UI_COLORS["text"],
            bordercolor=UI_COLORS["border"],
            lightcolor=UI_COLORS["border"],
            darkcolor=UI_COLORS["border"],
            padding=(7, 5),
        )
        style.configure(
            "TCombobox",
            fieldbackground=UI_COLORS["surface"],
            foreground=UI_COLORS["text"],
            bordercolor=UI_COLORS["border"],
            padding=(6, 5),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", UI_COLORS["surface"])],
            selectbackground=[("readonly", UI_COLORS["selection"])],
            selectforeground=[("readonly", UI_COLORS["text"])],
        )
        style.configure(
            "TNotebook",
            background=UI_COLORS["background"],
            borderwidth=0,
            tabmargins=(4, 4, 4, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background=UI_COLORS["surface_alt"],
            foreground=UI_COLORS["muted"],
            padding=(14, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", UI_COLORS["surface"]), ("active", UI_COLORS["selection"])],
            foreground=[("selected", UI_COLORS["primary"]), ("active", UI_COLORS["primary"])],
        )
        style.configure(
            "Treeview",
            background=UI_COLORS["surface"],
            fieldbackground=UI_COLORS["surface"],
            foreground=UI_COLORS["text"],
            rowheight=29,
            bordercolor=UI_COLORS["border"],
            borderwidth=1,
            relief="solid",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=UI_COLORS["primary"],
            foreground="#FFFFFF",
            relief="flat",
            padding=(8, 7),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", UI_COLORS["selection"])],
            foreground=[("selected", UI_COLORS["text"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=UI_COLORS["surface_alt"],
            troughcolor=UI_COLORS["background"],
            bordercolor=UI_COLORS["background"],
            arrowcolor=UI_COLORS["primary"],
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=UI_COLORS["surface_alt"],
            troughcolor=UI_COLORS["background"],
            bordercolor=UI_COLORS["background"],
            arrowcolor=UI_COLORS["primary"],
        )

    def on_close(self):
        try:
            self.db.close()
        finally:
            self.destroy()

    def show_login(self):
        self.clear_window()
        self.user = None
        self.login_view = Login(
            self,
            authenticate=self.db.authenticate,
            on_authenticated=self._on_authenticated,
        )
        self.login_view.pack(expand=True)
        self.login_view.password_entry.focus_set()

    def _on_authenticated(self, user):
        self.user = user
        self.show_main()

    def show_main(self):
        if self.user is None:
            self.show_login()
            return
        self.clear_window()
        shell = ttk.Frame(self, style="Workspace.TFrame")
        shell.pack(fill="both", expand=True)
        sidebar = ttk.Frame(shell, style="Sidebar.TFrame", width=245, padding=(18, 22))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="MIS TRAPITOS", style="SidebarBrand.TLabel").pack(anchor="w")
        ttk.Label(sidebar, text="Gestión de tienda", style="SidebarMuted.TLabel").pack(anchor="w", pady=(2, 22))
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=(0, 18))
        ttk.Label(sidebar, text="MÓDULOS", style="SidebarSection.TLabel").pack(anchor="w", pady=(0, 8))
        navigation = ttk.Frame(sidebar, style="Sidebar.TFrame")
        navigation.pack(fill="x")
        modules = (
            ("Productos", "Productos"),
            ("Ventas", "Ventas"),
            ("Contactos", "Contactos y usuarios"),
            ("Promociones", "Promociones"),
            ("Devoluciones", "Devoluciones y cancelaciones"),
            ("Reportes", "Reportes"),
            ("Rastreabilidad", "Rastreabilidad"),
        )
        self.navigation_buttons = []
        for index, (label, _) in enumerate(modules):
            button = ttk.Button(
                navigation,
                text=label,
                style="SidebarActive.TButton" if index == 0 else "Sidebar.TButton",
                command=lambda tab_index=index: self._select_module(tab_index),
            )
            button.pack(fill="x", pady=2)
            self.navigation_buttons.append(button)
        sidebar_footer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        sidebar_footer.pack(side="bottom", fill="x", pady=(20, 0))
        ttk.Separator(sidebar_footer, orient="horizontal").pack(fill="x", pady=(0, 16))
        ttk.Label(sidebar_footer, text="SESIÓN ACTIVA", style="SidebarSection.TLabel").pack(anchor="w")
        ttk.Label(sidebar_footer, text=self.user["name"], style="SidebarBrand.TLabel").pack(anchor="w", pady=(5, 0))
        ttk.Label(sidebar_footer, text=self.user["role"], style="SidebarMuted.TLabel").pack(anchor="w")
        ttk.Button(
            sidebar_footer,
            text="Cerrar sesión",
            style="SidebarLogout.TButton",
            command=self.show_login,
        ).pack(fill="x", pady=(12, 0))

        workspace = ttk.Frame(shell, style="Workspace.TFrame")
        workspace.pack(side="left", fill="both", expand=True)
        workspace_header = ttk.Frame(workspace, style="WorkspaceHeader.TFrame", padding=(28, 16))
        workspace_header.pack(fill="x")
        ttk.Label(workspace_header, textvariable=self.module_title, style="WorkspaceTitle.TLabel").pack(side="left")
        ttk.Label(
            workspace_header,
            text=f"Usuario: {self.user['name']}  •  Rol: {self.user['role']}",
            style="WorkspaceMuted.TLabel",
        ).pack(side="right")
        content = ttk.Frame(workspace, style="Content.TFrame", padding=(20, 10, 20, 18))
        content.pack(fill="both", expand=True)
        nb = ttk.Notebook(content, style="Hidden.TNotebook")
        nb.pack(fill="both", expand=True)
        self.main_notebook = nb
        self.make_products_tab(nb)
        self.ventas_ui = VentasUI(nb, self.db, self.user, on_venta_registrada=self.refresh_products)
        nb.add(self.ventas_ui, text="Ventas")
        self.contactos_ui = ContactosUI(nb, self.db)
        nb.add(self.contactos_ui, text="Contactos y usuarios")
        self.promociones_ui = PromocionesUI(nb, self.db)
        nb.add(self.promociones_ui, text="Promociones")
        self.devoluciones_ui = DevolucionesUI(
            nb, self.db, on_inventario_actualizado=self.refresh_products
        )
        nb.add(self.devoluciones_ui, text="Devoluciones y cancelaciones")
        self.make_reports_tab(nb)
        self.make_traceability_tab(nb)
        nb.bind("<<NotebookTabChanged>>", self._on_module_changed)
        self._select_module(0)

    def _select_module(self, tab_index):
        if self.main_notebook is None:
            return
        self.main_notebook.select(tab_index)
        self._on_module_changed()

    def _on_module_changed(self, event=None):
        if self.main_notebook is None:
            return
        selected = self.main_notebook.index(self.main_notebook.select())
        titles = (
            "Productos",
            "Ventas",
            "Contactos y usuarios",
            "Promociones",
            "Devoluciones y cancelaciones",
            "Reportes",
            "Rastreabilidad",
        )
        if 0 <= selected < len(titles):
            self.module_title.set(titles[selected])
        for index, button in enumerate(self.navigation_buttons):
            button.configure(style="SidebarActive.TButton" if index == selected else "Sidebar.TButton")

    def clear_window(self):
        for child in self.winfo_children():
            child.destroy()
        self.productos_ui = None
        self.contactos_ui = None
        self.main_notebook = None
        self.navigation_buttons = []
        self.login_view = None
        self.ventas_ui = None
        self.promociones_ui = None
        self.devoluciones_ui = None

    def make_products_tab(self, nb):
        self.productos_ui = ProductosUI(nb, self.db)
        nb.add(self.productos_ui, text="Productos")

    def refresh_products(self):
        """Actualiza productos tras una venta, devolucion o cancelacion."""
        if self.productos_ui is not None:
            self.productos_ui.actualizar_inventario()

    def make_reports_tab(self, nb):
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Reportes")
        controls = ttk.LabelFrame(tab, text="Consulta", padding=10)
        controls.pack(fill="x")
        ttk.Label(controls, text="Reporte").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.report_combo = ttk.Combobox(controls, values=REPORTS, state="readonly", width=48)
        self.report_combo.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        self.report_combo.set(REPORTS[0])
        self.report_param = add_labeled_entry(controls, "Parametro", 0, 2, width=30)
        ttk.Button(controls, text="Ejecutar", command=self.run_report).grid(row=0, column=4, padx=4, pady=4)
        ttk.Button(controls, text="Exportar CSV", command=self.export_report_csv).grid(row=0, column=5, padx=4, pady=4)
        self.report_hint = ttk.Label(controls, text="Parametro se usa en reportes por categoria, proveedor, cliente, precio o stock bajo.")
        self.report_hint.grid(row=1, column=0, columnspan=6, sticky="w", padx=4)
        table = ttk.LabelFrame(tab, text="Resultado", padding=5)
        table.pack(fill="both", expand=True, pady=8)
        self.report_tree = make_tree(table, ("resultado",), height=18)
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
        config_tree = make_tree(upper, ("id", "elemento", "valor", "estado"), height=5)
        for item in CONFIG_ITEMS:
            config_tree.insert("", tk.END, values=item)
        lower = ttk.LabelFrame(tab, text="Matriz de rastreabilidad", padding=5)
        lower.pack(fill="both", expand=True, pady=8)
        trace_tree = make_tree(lower, ("id", "requerimiento", "modulo", "prueba"), height=18)
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
