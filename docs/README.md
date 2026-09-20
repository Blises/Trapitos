# Índice y coordinación de la documentación del sistema

## Mis Trapitos — Épica #3

| Control documental | Valor |
| --- | --- |
| Identificador | MT-DOC-001 |
| Versión | 1.0 |
| Épica asociada | [#3 — Creación y/o actualización de documentación del sistema](https://github.com/SQEquipo3/Trapitos/issues/3) |
| Alcance | Agrupar y coordinar SAD, SDD, Test Plan y Test Report. |
| Estado del conjunto documental | SAD y SDD disponibles; Test Plan y Test Report pendientes de incorporación. |
| Línea base del inventario inicial | Commit `8b16569515380285a419d839eabef67570e7ea60`. |

## 1. Propósito y alcance

Este índice centraliza los documentos formales de Mis Trapitos y establece su relación con las historias de trabajo, las fuentes del sistema y las evidencias de validación. Su finalidad es facilitar la coordinación y el seguimiento de la trazabilidad solicitada por la épica #3.

La épica actúa como contenedora. La elaboración y aceptación de cada documento se gestiona en su historia correspondiente; este índice registra sus entregables, dependencias y pendientes. La disponibilidad de un archivo, el cierre de una historia y la aprobación formal de un documento son estados distintos.

## 2. Catálogo documental y seguimiento

| Documento | Historia asociada | Entregable disponible | Función dentro del conjunto | Estado documental y siguiente acción |
| --- | --- | --- | --- | --- |
| Software Architecture Document (SAD) | [#6](https://github.com/SQEquipo3/Trapitos/issues/6) | [SAD.md](SAD.md), versión 1.0. | Justificar tecnologías, arquitectura, capas, distribución y operación local. | Disponible. Mantener sus decisiones, supuestos y referencias a la implementación al actualizar el sistema. |
| Software Design Document (SDD) | [#5](https://github.com/SQEquipo3/Trapitos/issues/5) | [SDD.md](SDD.md), versión 1.0. | Detallar módulos, interfaces, datos y secuencias; relacionarlos con requisitos. | Disponible. Su control documental indica revisión final del equipo pendiente; registrar la resolución en esa historia. |
| SW Test Plan | [#4](https://github.com/SQEquipo3/Trapitos/issues/4) | Pendiente; sin archivo formal en la línea base del inventario. | Definir alcance, casos, prioridades, entorno y criterios de prueba. | Elaborar en su historia e incorporar aquí la ruta, versión y estado de revisión. |
| Test Report | [#1](https://github.com/SQEquipo3/Trapitos/issues/1) | Pendiente; sin archivo formal en la línea base del inventario. | Registrar ejecución, resultados, incidencias y evidencias respecto del plan. | Elaborar en su historia cuando existan un plan identificado y evidencia de ejecución; incorporar aquí el entregable. |

La épica comunicada registra dos de cuatro historias completadas. El inventario local confirma la presencia de dos de los cuatro documentos; esa proporción no mide cobertura de requisitos, porcentaje de pruebas aprobadas ni preparación para producción. El estado vigente de las historias se consulta en sus enlaces de GitHub; las versiones y aprobaciones documentales se consultan en cada entregable.

## 3. Dependencias y coordinación

| Etapa | Insumos | Entrega a la siguiente etapa | Coordinación propuesta por función |
| --- | --- | --- | --- |
| Arquitectura | Alcance y requisitos del sistema; restricciones operativas. | SAD con decisiones, supuestos y escenarios de aceptación. | Arquitectura y equipo de desarrollo. |
| Diseño detallado | SAD y código de la versión examinada. | SDD con componentes, contratos, datos y trazabilidad. | Equipo de desarrollo y revisión técnica. |
| Planificación de pruebas | Requisitos, SAD, SDD y brechas identificadas. | Test Plan con casos identificables, prioridades y criterios verificables. | Responsable de calidad y equipo de desarrollo. |
| Reporte de pruebas | Test Plan, versión probada y evidencia de ejecución. | Test Report con resultados por caso, incidencias y limitaciones. | Responsable de calidad y revisión del equipo. |

Las funciones anteriores orientan la coordinación; no asignan personas ni sustituyen a los responsables registrados en GitHub. Un cambio de requisitos o arquitectura requiere revisar los documentos dependientes. Un fallo de prueba puede motivar una revisión del diseño o del plan, conservando la evidencia del resultado original.

## 4. Trazabilidad entre documentos

La cadena de referencia del conjunto será: **requisito → decisión de arquitectura → componente de diseño → caso de prueba → resultado y evidencia**. Los identificadores existentes deben conservarse para permitir el seguimiento en ambos sentidos.

| Elemento que se debe vincular | Fuente disponible | Relación documental | Pendiente de coordinación |
| --- | --- | --- | --- |
| RF-01–RF-26 y RNF-01 | `TRACEABILITY` en el [código principal](../mis_trapitos_app_v7.py). | Alcance y correspondencia en el SAD; matriz por requisito en la sección 9 del SDD. | Vincular cada requisito con casos identificados del Test Plan y sus resultados en el Test Report. |
| Decisiones de arquitectura | ADR-01–ADR-05 del [SAD](SAD.md). | Contexto, módulos y contratos actuales/propuestos en el SDD. | Identificar los casos que comprueban cada decisión aplicable a la versión evaluada. |
| Componentes e interfaces | MOD-01–MOD-05, UI-01–UI-10 y OP-01–OP-07 del [SDD](SDD.md). | Relación con código, modelo de datos y requisitos. | Asociar los casos del plan con los componentes que ejercitan. |
| Escenarios de validación | PA-01–PA-12 del SAD y VD-01–VD-10 del SDD. | Condiciones de validación del diseño, incluidas capacidades futuras. | Incorporar su selección al plan y distinguir ejecutados, pendientes y no aplicables. |
| Evidencia de pruebas existente | [Pruebas locales de productos](../tests/test_ui_productos.py) y registro de revisión del SDD. | Antecedentes para planificar y documentar la validación. | Registrar una ejecución identificable en el Test Report; la existencia de pruebas no sustituye ese documento. |
| Observaciones y brechas | Sección 11 del SDD y riesgos del SAD. | Limitaciones que condicionan diseño y aceptación. | Dar seguimiento en las historias correspondientes y enlazar la evidencia de resolución cuando exista. |

La cadena está documentada hasta el diseño y dispone de antecedentes de pruebas locales. Su trazabilidad hasta un plan y un reporte formales permanece pendiente. Los criterios específicos de la rúbrica deberán asociarse a estas evidencias cuando el equipo disponga de su texto; no se declara cumplimiento integral de una rúbrica no incorporada al repositorio.

## 5. Procedimiento de actualización documental

1. Identificar la historia y el documento afectados, así como la versión de código o requisito que origina el cambio.
2. Actualizar el documento correspondiente, conservando identificadores y registrando versión, motivo y referencias de la revisión.
3. Revisar el impacto sobre los otros documentos mediante las dependencias de las secciones 3 y 4.
4. Verificar enlaces, coherencia de nombres y correspondencia entre afirmaciones y evidencia. Distinguir implementación actual, diseño propuesto y validación pendiente.
5. Actualizar el catálogo de este índice con el entregable y su estado real. Registrar aprobaciones únicamente cuando hayan sido efectuadas por el equipo responsable.
6. Mantener en el commit la referencia a la historia atendida y, cuando corresponda, a la épica #3.

## 6. Lista de seguimiento del conjunto documental

Esta lista facilita la coordinación de la épica; no reemplaza los criterios de aceptación de las historias hijas.

- [x] Centralizar los cuatro documentos y sus historias asociadas en un único índice.
- [x] Enlazar SAD y SDD disponibles desde el catálogo.
- [x] Establecer dependencias, cadena de trazabilidad y procedimiento de actualización.
- [ ] Incorporar el Test Plan aceptado en su historia correspondiente.
- [ ] Incorporar el Test Report y sus evidencias conforme al plan identificado.
- [ ] Verificar la trazabilidad completa entre requisitos, diseño, casos y resultados.
- [ ] Registrar la revisión del conjunto frente a la rúbrica y resolver los pendientes de aceptación documental.

La creación de este índice organiza el seguimiento solicitado por la épica. Su cierre global dependerá de los documentos y validaciones pendientes; no se deduce de la existencia del índice.

## 7. Historial de revisiones

| Versión | Descripción |
| --- | --- |
| 1.0 | Inventario inicial de SAD, SDD, Test Plan y Test Report; relación con historias, dependencias, trazabilidad y seguimiento de pendientes. |

[Volver a la descripción del proyecto](../README.md)
