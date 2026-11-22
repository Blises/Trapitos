
"""Creación y migraciones versionadas del esquema SQLite."""

# ============================================================
# CREACIÓN DE TABLAS
# ============================================================

def create_schema(db):
    """
    Crea todas las tablas de la aplicación si todavía no existen.

    Las modificaciones posteriores de la estructura se realizan
    mediante las migraciones numeradas.
    """

    db.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            phone TEXT,
            address TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            city_region TEXT,
            preferences TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
            sale_price REAL NOT NULL CHECK(sale_price >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0),
            supplier_id INTEGER,
            entry_date TEXT NOT NULL,
            brand TEXT,
            season TEXT,
            image_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        );

        CREATE TABLE IF NOT EXISTS promotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            discount_percent REAL NOT NULL
                CHECK(discount_percent >= 0 AND discount_percent <= 100),
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_datetime TEXT NOT NULL,
            customer_id INTEGER,
            employee_id INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            sale_discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVA',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL,
            promo_discount_percent REAL NOT NULL DEFAULT 0,
            line_total REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            movement_datetime TEXT NOT NULL,
            reason TEXT NOT NULL,
            related_sale_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (related_sale_id) REFERENCES sales(id)
        );

        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            return_datetime TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS cancellations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            cancel_datetime TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        );

        CREATE TABLE IF NOT EXISTS lan_requests (
            request_key TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL,
            sale_id INTEGER NOT NULL REFERENCES sales(id),
            employee_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    db.conn.commit()


# ============================================================
# MIGRACIONES
# ============================================================

def migracion_1(db):
    """
    Migración 1:
    Agrega products_supplied y last_order_date a suppliers.

    Comprueba las columnas existentes para poder trabajar
    con bases antiguas que ya tengan alguna de ellas.
    """

    columnas = [
        fila[1]
        for fila in db.query("PRAGMA table_info(suppliers)")
    ]

    if "products_supplied" not in columnas:
        db.execute(
            "ALTER TABLE suppliers ADD COLUMN products_supplied TEXT"
        )

    if "last_order_date" not in columnas:
        db.execute(
            "ALTER TABLE suppliers ADD COLUMN last_order_date TEXT"
        )


# ============================================================
# REGISTRO DE MIGRACIONES
# ============================================================

# Las migraciones se ejecutan en orden ascendente.
# Cuando se agreguen nuevas migraciones, se deben numerar
# consecutivamente: 2, 3, 4, etc.

MIGRACIONES = [
    (1, migracion_1),
]


# ============================================================
# EJECUCIÓN DE MIGRACIONES
# ============================================================

def migrate_schema(db):
    """
    Consulta la versión de la base de datos y ejecuta
    únicamente las migraciones pendientes.

    PRAGMA user_version almacena la versión actual del esquema.
    """

    version_actual = db.scalar("PRAGMA user_version")

    if version_actual is None:
        version_actual = 0

    ultima_version = MIGRACIONES[-1][0] if MIGRACIONES else 0

    # No permite utilizar una base de datos más nueva
    # que las migraciones conocidas por esta aplicación.
    if version_actual > ultima_version:
        raise RuntimeError(
            f"La base de datos tiene la versión {version_actual}, "
            f"pero esta aplicación solo admite hasta la versión "
            f"{ultima_version}."
        )

    # Inicia una transacción para que las migraciones
    # se apliquen juntas y puedan revertirse si ocurre un error.
    db.conn.execute("BEGIN IMMEDIATE")

    try:
        for numero, funcion in MIGRACIONES:

            # Solo ejecuta migraciones posteriores a la versión actual.
            if numero > version_actual:

                funcion(db)

                # Guarda la nueva versión después de cada migración.
                db.conn.execute(
                    f"PRAGMA user_version = {numero}"
                )

        # Confirma todos los cambios.
        db.conn.commit()

    except Exception:
        # Revierte los cambios si alguna migración falla.
        db.conn.rollback()
        raise
