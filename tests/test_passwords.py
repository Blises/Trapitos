import hashlib

from mis_trapitos.data.repositories import empleados as empleados_repo
from tests.tc import tc
from utils import hash_password, verify_password


@tc("UTS_SEG_01")
def test_dos_hashes_de_misma_password_son_diferentes():
    hash1 = hash_password("1234")
    hash2 = hash_password("1234")

    assert hash1 != hash2


@tc("UTS_SEG_01")
def test_verificar_password_correcta():
    password_hash = hash_password("1234")

    assert verify_password("1234", password_hash)


@tc("UTS_SEG_01")
def test_verificar_password_incorrecta():
    password_hash = hash_password("1234")

    assert not verify_password("0000", password_hash)


@tc("UTS_SEG_01")
def test_login_acepta_hash_sha256_antiguo(db, hash_sha256_antiguo):
    antiguo = hash_sha256_antiguo("1234")

    empleado_id = empleados_repo.guardar(
        db, None, "Administrador", "admin_antiguo", "1234", "Administrador"
    )

    # Simular una cuenta que todavía tiene el hash antiguo.
    db.execute(
        "UPDATE employees SET password_hash=? WHERE id=?",
        (antiguo, empleado_id),
    )

    empleado = empleados_repo.autenticar(db, "admin_antiguo", "1234")

    assert empleado is not None


@tc("UTS_SEG_01")
def test_login_migra_hash_antiguo_a_pbkdf2(db, hash_sha256_antiguo):
    antiguo = hash_sha256_antiguo("1234")

    empleado_id = empleados_repo.guardar(
        db, None, "Administrador", "admin_migrar", "1234", "Administrador"
    )

    db.execute(
        "UPDATE employees SET password_hash=? WHERE id=?",
        (antiguo, empleado_id),
    )

    empleado = empleados_repo.autenticar(db, "admin_migrar", "1234")

    nuevo_hash = db.scalar(
        "SELECT password_hash FROM employees WHERE id=?",
        (empleado_id,),
    )

    assert empleado is not None
    assert nuevo_hash != antiguo
    assert nuevo_hash.startswith("pbkdf2_sha256$")
    assert verify_password("1234", nuevo_hash)


@tc("UTS_SEG_01")
def test_login_rechaza_password_incorrecta(db):
    empleados_repo.guardar(
        db, None, "Administrador", "admin_incorrecto", "1234", "Administrador"
    )

    empleado = empleados_repo.autenticar(
        db, "admin_incorrecto", "0000"
    )

    assert empleado is None