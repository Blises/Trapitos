
"""Repositorio de empleados.

Todas las funciones reciben el objeto Database (data/database.py).
"""

from utils import (
    hash_password,
    verify_password,
    needs_password_rehash,
    now_text,
)


def listar(db):
    """Filas para la tabla de empleados."""
    return db.query(
        """
        SELECT id, name AS nombre, username AS usuario, role AS rol
        FROM employees
        ORDER BY id DESC
        """
    )


def autenticar(db, username, password):
    """
    Comprueba las credenciales del empleado.

    Si la contraseña utiliza el SHA-256 antiguo,
    la actualiza automáticamente al formato PBKDF2.
    """

    # Buscar al empleado únicamente por su nombre de usuario.
    empleado = db.one(
        "SELECT * FROM employees WHERE username=?",
        (username,),
    )

    # Si el usuario no existe, rechazar el acceso.
    if empleado is None:
        return None

    # Verificar la contraseña utilizando el hash almacenado.
    if not verify_password(password, empleado["password_hash"]):
        return None

    # Comprobar si la contraseña todavía utiliza el formato antiguo.
    if needs_password_rehash(empleado["password_hash"]):

        # Generar un nuevo hash con una sal aleatoria.
        nuevo_hash = hash_password(password)

        # Actualizar la contraseña en la base de datos.
        db.execute(
            """
            UPDATE employees
            SET password_hash = ?
            WHERE id = ?
            """,
            (nuevo_hash, empleado["id"]),
        )

        # Recuperar el empleado con su nuevo hash.
        empleado = db.one(
            "SELECT * FROM employees WHERE id=?",
            (empleado["id"],),
        )

    # Devolver los datos del empleado autenticado.
    return empleado


def primero(db):
    return db.one("SELECT * FROM employees ORDER BY id LIMIT 1")


def obtener_por_id(db, employee_id):
    return db.one(
        "SELECT * FROM employees WHERE id=?",
        (employee_id,),
    )


def guardar(db, employee_id, name, username, password, role):
    """Alta o edición de un empleado."""

    if employee_id:
        if password:
            db.execute(
                """
                UPDATE employees
                SET name=?, username=?, password_hash=?, role=?
                WHERE id=?
                """,
                (
                    name,
                    username,
                    hash_password(password),
                    role,
                    employee_id,
                ),
            )
        else:
            db.execute(
                """
                UPDATE employees
                SET name=?, username=?, role=?
                WHERE id=?
                """,
                (name, username, role, employee_id),
            )

        return employee_id

    cur = db.execute(
        """
        INSERT INTO employees
        (name, username, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            username,
            hash_password(password or "1234"),
            role,
            now_text(),
        ),
    )

    return cur.lastrowid


def eliminar(db, employee_id):
    """Borra el empleado."""
    db.execute(
        "DELETE FROM employees WHERE id=?",
        (employee_id,),
    )
