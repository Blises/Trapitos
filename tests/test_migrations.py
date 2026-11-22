
import sqlite3

from mis_trapitos.data.database import Database
from mis_trapitos.data.schema import migrate_schema


def test_base_nueva_aplica_migracion(tmp_path):
    """Una base nueva debe terminar con la versión 1."""

    ruta = tmp_path / "nueva.db"

    db = Database(str(ruta), load_examples=False)

    version = db.scalar("PRAGMA user_version")

    columnas = [
        fila[1]
        for fila in db.query("PRAGMA table_info(suppliers)")
    ]

    assert version == 1
    assert "products_supplied" in columnas
    assert "last_order_date" in columnas

    db.close()


def test_base_antigua_conserva_datos(tmp_path):
    """Una base antigua sin versión debe conservar sus datos."""

    ruta = tmp_path / "antigua.db"

    # Simula una base antigua que todavía no tiene
    # las columnas agregadas por la migración 1.
    conexion = sqlite3.connect(ruta)

    conexion.execute("""
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            phone TEXT,
            address TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conexion.execute("""
        INSERT INTO suppliers
        (name, phone, address, created_at)
        VALUES (?, ?, ?, ?)
    """, ("Proveedor antiguo", "1234567890", "Centro", "2026-01-01"))

    conexion.commit()
    conexion.close()

    # Al abrir la base, Database debe aplicar la migración.
    db = Database(str(ruta), load_examples=False)

    proveedor = db.one(
        "SELECT * FROM suppliers WHERE name = ?",
        ("Proveedor antiguo",)
    )

    columnas = [
        fila[1]
        for fila in db.query("PRAGMA table_info(suppliers)")
    ]

    assert db.scalar("PRAGMA user_version") == 1
    assert proveedor is not None
    assert proveedor["phone"] == "1234567890"
    assert "products_supplied" in columnas
    assert "last_order_date" in columnas

    db.close()


def test_migraciones_idempotentes(tmp_path):
    """Ejecutar las migraciones dos veces no debe duplicar cambios."""

    ruta = tmp_path / "idempotencia.db"

    db = Database(str(ruta), load_examples=False)

    migrate_schema(db)
    migrate_schema(db)

    version = db.scalar("PRAGMA user_version")

    columnas = [
        fila[1]
        for fila in db.query("PRAGMA table_info(suppliers)")
    ]

    assert version == 1
    assert columnas.count("products_supplied") == 1
    assert columnas.count("last_order_date") == 1

    db.close()
