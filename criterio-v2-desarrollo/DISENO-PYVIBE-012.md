# PYVIBE-012: separar retención y supervisión (propuesta de diseño, sin implementar)

**Estado:** propuesta del 2026-11-03 (decisión 4 de Joaquín). No se implementa en `pyvibe-pro` ni en ningún analizador hasta que Joaquín la apruebe. Cada regla resultante necesitará su propia validación (`../tc5-borrador/PREREGISTRATION-BORRADOR.md`).

## Problema

Hoy PYVIBE-012 alerta de un único hecho detectado: el resultado de `asyncio.create_task(...)` o `asyncio.ensure_future(...)` se descarta. Su mensaje mezcla dos impactos: (i) la tarea puede ser recolectada antes de terminar; (ii) una excepción suya nunca se recupera.

En TC4 (`PROPUESTA-v2.md` §2), el código respalda los mecanismos así:

| Mecanismo | Casos en TC4 (n = 55) |
|---|---|
| b1, pérdida por no retención | 0 |
| b2, excepción sin supervisión | 12 |
| b2 y b3 (además, sin recuperación) | 6 |

La detección actual no distingue ninguno de esos casos.

## Regla de diseño: una detección, una alerta

**Separar el mensaje no autoriza dos alertas basadas en la misma detección.** Si la única evidencia es «se descarta la referencia», hay una sola alerta. Su categoría es «incumplimiento de recomendación documentada de uso seguro» y su gravedad, WARNING.

Una segunda alerta sobre la misma llamada solo es admisible si tiene su propia condición de detección y su propia evidencia, independientes de la primera.

## Propuesta

### R — Retención (sustituye al PYVIBE-012 actual)

- **Detección:** se descarta el resultado de `create_task`/`ensure_future`, no se guarda en ninguna estructura y no se le añade ningún `add_done_callback` que lo retenga.
- **Evidencia del mensaje:** la línea de la llamada y la ausencia de referencia.
- **Categoría:** incumplimiento de recomendación documentada de uso seguro (documentación de Python, `asyncio.create_task`). **Gravedad:** WARNING.
- **Mensaje:** solo lo que la detección demuestra, que se incumple la recomendación de retención. No afirma pérdida ni excepciones perdidas.
- **Agravante opcional, con detección propia:** la corrutina espera un awaitable creado y referenciado solo dentro de la propia tarea (un `Future`/`Event` local que nada más retiene). Solo eso respalda b1 (pérdida por no retención). Exige resolver la corrutina en el mismo módulo y seguir sus `await`; si no se puede, no se afirma.

### S — Supervisión (regla nueva, independiente)

- **Detección propia, distinta de R:**
  1. la corrutina lanzada se resuelve estáticamente (mismo módulo o import directo);
  2. su cuerpo tiene al menos una llamada que puede lanzar en operación normal (E/S de red, de disco o de base de datos; lista de APIs por lenguaje y biblioteca) fuera de un `try` que la contenga;
  3. no hay supervisión: ni `add_done_callback` que lea `exception()`, ni `TaskGroup`, ni `await`/`gather` de la tarea en otra parte, ni un manejador de excepciones del loop configurado en el repositorio.
- **Evidencia del mensaje:** el `file:line` de la llamada que escapa y la ausencia de supervisión. No basta con «se descarta la referencia».
- **Gravedad:** WARNING. Si llega a validarse, la gravedad la decide la selección.
- **Recuperación (b3) como dato del informe, no como condición de alerta:** si el código pone un estado antes de la llamada que escapa y nada lo restaura, o si es un bucle de fondo sin reinicio, el hallazgo lo indica como «sin recuperación en el código». Ese dato no crea una tercera alerta.

### Si R y S coinciden en la misma llamada

Se emite un solo hallazgo con dos evidencias separadas: la retención de R y la ruta de excepción de S. Cada evidencia se marca como satisfecha o no satisfecha según su propia condición. Las métricas de cada regla se calculan solo con los casos en que su condición se cumplió.

## Qué no cambia

- La evaluación de TC1–TC4 y sus veredictos publicados.
- PYVIBE-014, que sigue el mismo patrón y se trataría igual en una iteración posterior.
- Los analizadores: nada de esto está implementado.

## Limitaciones conocidas

- S necesita resolver la corrutina y saber qué llamadas pueden lanzar. Cuando no pueda (corrutinas dinámicas, decoradores, bibliotecas desconocidas), no alerta: la falta de evidencia no es un hallazgo.
- El agravante de R es raro: no aparece en ningún caso de TC4. Hay que validarlo antes de afirmarlo en un informe.
