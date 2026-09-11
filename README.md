# Mis Trapitos

Sistema local de gestión de una tienda de ropa desarrollado en Python con Tkinter y SQLite. El prototipo actual se encuentra en `mis_trapitos_app_v7.py`.

## Módulo de productos

`ui_productos.py` contiene `ProductosUI`, una pestaña Tkinter que administra el formulario de productos y variantes por talla/color, sus validaciones, imágenes, inventario y exportación CSV. Recibe la instancia de `Database` de la aplicación; la persistencia y las transacciones permanecen en esa clase.

`App` incorpora la pestaña y delega `refresh_products()` a `ProductosUI.actualizar_inventario()`. Las altas, ediciones, ventas, devoluciones y cancelaciones exitosas actualizan las existencias en la tabla. Cuando cambia el stock del producto seleccionado, también se actualiza su formulario sin descartar las ediciones pendientes de otros campos. Esta actualización ocurre dentro de la aplicación local.

Para ejecutar la aplicación, conservar ambos archivos Python en la misma carpeta y utilizar `python mis_trapitos_app_v7.py` con Tkinter y Pillow disponibles.

## Pruebas de regresión

```sh
python -m unittest discover -s tests -v
```

Las pruebas utilizan widgets Tkinter reales con ventanas ocultas y bases SQLite temporales, sin cargar los datos de demostración. Requieren una sesión gráfica con Tk y Pillow. Cubren productos, variantes, validaciones, imágenes, CSV, selección, cambios de sesión y actualización del inventario después de ventas, devoluciones y cancelaciones.

## Documentación

- [Documento de Arquitectura de Software (SAD)](docs/SAD.md): decisiones tecnológicas, capas, patrones, distribución propuesta para 7 terminales y operación sin internet mediante una red local.

El SAD distingue la implementación actual de la arquitectura propuesta. El prototipo todavía no incluye el servicio LAN necesario para compartir de forma controlada una única base de datos entre las siete terminales.
