# Review log — test-corpus-2

Every piece of help received during the review, from whoever gives it (any Claude session or
other AI, including Joaquín's adviser). Only factual navigation is allowed: where a file is,
what a line contains, what a search returns. Never a verdict, an assessment or an opinion on
the case (PREREGISTRATION.md, "Assistance during the review"). The cards do not change.

| date | who | question | answer |
|---|---|---|---|
| 2026-10-15 | Joaquín | Empezó a mirar J001 con el método anterior (revisión completa por Joaquín); no registró veredicto. | — |
| 2026-10-15 | Claude (asesor) | ¿Qué tengo que mirar en una ficha? | Explicación general del método (3 condiciones y cómo filtrar la búsqueda literal), sin referencia a ningún caso concreto. |
| 2026-10-15 | Claude (asesor) | J001: ¿cuál es la línea marcada? | La marcada con ">": línea 41, `Thread.sleep(millis);`, coincide con Location SampleBackground.java:41. |
| 2026-10-15 | Claude (asesor) | Traducción al español de la tabla de criterios del pre-registro (antes de empezar). | Traducción de apoyo; manda el texto en inglés del pre-registro. |
| 2026-10-24 | Claude (asesor) | Fichas J015, J038, J056, J036, J001, J020, J023, J052, J021, P145, P083, P099, P098, P072: ¿qué contiene la ficha? | Además de la línea marcada y la búsqueda literal, añadió por su cuenta un bloque de «contexto» con valoraciones (p. ej. «el sleep es intencional», «es un smoke test, no producción», «impacto práctico mínimo», «el catch silencioso pierde el audit log»). Eso excede la navegación factual permitida. Los veredictos de estos 14 casos se dieron después de leerlo. |
| 2026-10-24 | Claude (asesor) | Resumen provisional de precisión Java tras 9 casos | Dio un porcentaje provisional (75 %, luego corregido a 7 TP / 2 FP = 77,8 %). Es una valoración, no navegación; no cuenta como dato (n < 50). |
| 2026-10-24 | Joaquín | Overstated de los 14 casos | Primera tabla: solo J015 = Sí. Revisada tras señalar una inconsistencia de criterio: Sí en J015, J038, J036, J020, J023, J052, J021, P098; No en el resto. |
| 2026-10-24 | Claude (asesor) | P002 (tras registrar U) | Recordó la definición de U del pre-registro (el repo no permite decidir; p. ej. llamador fuera del repo), sin valorar el caso. Joaquín revisó y cambió U a FP; Claude lo sustituyó literal en la hoja. |
| 2026-10-24 | Claude (asesor) | P077 | Registró U literal; indicó cómo buscar el llamador (navegación); Joaquín lo revisó y lo cambió a TP; Claude lo sustituyó literal. No valoró el caso. |
| 2026-10-24 | Claude (asesor) | P145–P153 (27) | Transcribió los veredictos de Joaquín a REVIEW-SHEET.md de forma literal, sin modificarlos. |
