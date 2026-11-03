# Pre-registro de test-corpus-5: BORRADOR, sin ejecutar

**Estado:** borrador del 2026-11-03 (decisión 8 de Joaquín). **TC5 está aparcado** por la decisión de proyecto del mismo día (decisión 9; `~/vibe-guard`, `DECISIONS.md`), que pasa el trabajo a pilotos de auditoría.

- **Qué no es:** no está congelado ni es un pre-registro vigente.
- **Qué no se ha hecho:** no se ha buscado ningún repositorio, no se ha escaneado nada y no se ha creado `test-corpus-5/`.
- **Antes de usarlo:** Joaquín tiene que reactivarlo, y hay que cerrar los puntos marcados PENDIENTE antes de congelar.

## Objetivo

Validar la **regla de retención** de PYVIBE-012 (regla R de `../criterio-v2-desarrollo/DISENO-PYVIBE-012.md`), con el criterio `../REVIEW-CRITERIA-v2.md` en la versión que se cite al congelar.

- **No valida** la regla de supervisión (S). Si se implementa, S necesita su propio pre-registro.
- **No valida** ninguna regla Java. No hay ninguna regla Java seleccionada (`../criterio-v2-desarrollo/PROPUESTA-v2.md` §1–2), así que no hay prueba CRITICAL para Java; para ese lenguaje se acumula evidencia y se pre-registra después.

## Criterio de aceptación (por regla)

| Requisito | Valor |
|---|---|
| n (casos con veredicto de Joaquín) | ≥ 30 |
| Repositorios distintos | ≥ 5 |
| TP/n, con **U como no-TP** | ≥ 0,90 |

- **Registro aparte, que no decide la aceptación:**
  - el escenario de fallo, con sus tres mecanismos por separado: b1 pérdida por no retención, b2 excepción sin supervisión, b3 ausencia de recuperación (`../REVIEW-CRITERIA-v2.md` §3);
  - la causalidad: ningún recuento atribuye un fallo a la falta de retención sin evidencia propia;
  - la gravedad.
- **Sin CRITICAL automático.** TC5 solo validaría la detección de retención (R) **como WARNING**: si pasa, la regla queda validada con su evidencia publicada. Cualquier promoción a CRITICAL, por b1 o por la regla de supervisión S, necesita su propia regla, su propia selección por mecanismos (`../REVIEW-CRITERIA-v2.md` §2–3) y su propia confirmación. Hoy ninguna regla evaluada reúne los requisitos para CRITICAL automático.
- **Evidencia insuficiente** (n < 30, menos de 5 repos o un corpus sin terminar) significa que la regla **no queda validada** y sigue en WARNING.
- **Los mínimos son una decisión práctica, no una garantía estadística.** Se publican:
  - los intervalos de Wilson al 95 %;
  - los resultados por repositorio;
  - el número máximo de casos por repositorio.
- **Aviso obligatorio en los resultados:** si las cifras bajo v2 difieren de las publicadas bajo v1 (TC1–TC4), la diferencia refleja también el cambio de definición.

## Método (heredado de TC4, salvo lo indicado)

- **Población.** Revisión humana completa de todos los hallazgos de la regla en el corpus, como en TC4. No hay ningún mecanismo de inclusión que dependa del acuerdo de las IAs (la lección de TC3).
- **Triaje.** Se aplican la exclusión c2 de repositorios de estudio (`../REVIEW-CRITERIA.md` §2.4) y el filtro de repositorios de juguete de TC2–TC4.
- **Criterio de veredicto.** Se aplican §1–§3 de `../REVIEW-CRITERIA-v2.md`, copiados literalmente al congelar. FP solo si el repositorio demuestra que no se incumple nada; U si falta configuración decisiva.
- **Hoja de revisión, ayudas y registro de asistencia:** igual que en TC4. Solo se permite navegación factual.
- **Revisión IA opcional:** solo informativa y sellada antes de la hoja, como en TC4.

## PENDIENTE (antes de congelar)

- La búsqueda y el pool de repositorios Python, con su ordenación y su semilla.
- La versión congelada de la herramienta (`FROZEN.json`) con la regla R implementada y sus tests. Hoy no está implementada.
- Las semillas de la hoja y de la muestra IA.
- El presupuesto de tiempo de revisión y la regla de parada si no se alcanza n ≥ 30.
