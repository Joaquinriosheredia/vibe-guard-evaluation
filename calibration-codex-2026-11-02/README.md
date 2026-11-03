# Calibración Codex 2026-11-02: Codex frente a Claude y frente a Joaquín (TC2 + TC3 + TC4, 212 casos)

**Informativa.** No cambia ningún resultado publicado: ni `metrics.json`, ni `AI-COMPARISON.md`, ni ningún veredicto.

**Qué se hizo.** Codex CLI, con la sesión de ChatGPT de Joaquín, revisó con el protocolo **chain-v1** los 212 casos que tienen veredicto de Joaquín:

- TC2: 27 casos;
- TC3: 25 casos;
- TC4: 160 casos.

Se usaron las mismas instrucciones `../REVIEW-AI-INSTRUCTIONS.md` v1 y los mismos ejemplos `../calibration-v1-2026-10-28/examples-tc2.md`.

`table.py` compara tres configuraciones con las etiquetas originales de Joaquín y con las v1:

- **Claude proponente**: en TC4, la revisión sellada; en TC2 y TC3, la calibración del 28;
- **Codex solo**;
- el **consenso Claude = Codex**.

Detalles de la comparación:

- **Etiquetas v1:** `REVIEW-CRITERIA.md` v1 §6 cambia dos casos de FP a TP: TC2 J001 y TC3 P026. TC4 ya se revisó con v1.
- **Intervalos:** Wilson 95 %.
- **Respuesta inválida:** cuenta como desacuerdo.

Requisito previo comprobado: los tres `audit-joaquin.json` están en main (`167b2c6`) y coinciden con su `audit-joaquin.sha256`. `table.py` vuelve a comprobarlo, junto con el sha256 sellado de la revisión de Claude de TC4.

## Revisor

| | Codex (esta calibración) | Claude (comparado) |
|---|---|---|
| CLI | Codex CLI 0.166.0, `codex exec`, sesión de ChatGPT | Claude Code 2.1.312, suscripción Max |
| Modelo | `gpt-6.1-sol`, `model_reasoning_effort="medium"` (elección de Joaquín antes de la ejecución; el valor por defecto del CLI era razonamiento `none`) | `claude-opus-5-5` (por defecto del CLI) |
| Protocolo | chain-v1, solo proponente (`--reviewer-b none`), `--concurrency 3` | chain-v1, proponente (A) |
| Código | vibe-guard-scan `feat/review-codex-chain-v1` @ `950e59d` (subido antes de la ejecución, sin merge) | TC2/TC3: `d1aa18a`; TC4: `v0.4.1` |

En chain-v1 cada revisión de Codex tiene dos fases:

1. **Plan sin código:** se hace desde un directorio vacío, o desde el directorio del fichero de tarea si el prompt es largo.
2. **Revisión:** Codex lee el checkout del caso y usa la herramienta de llamadores, el servidor MCP `callers`, aprobado de antemano. La respuesta es una cadena de llamadas con un `path:line` por salto.

Se aplica la regla e: una cadena que no verifica pasa a U, nunca a FP.

Flags de `codex exec`:

- `--sandbox read-only --ephemeral --ignore-user-config --ignore-rules --json`;
- búsqueda web desactivada;
- desactivadas las funciones que añaden herramientas: apps, plugins, navegador, computer use, imágenes, sub-agentes, memorias y hooks.

## Aislamiento: Codex no puede leer los resultados

El sandbox `read-only` de Codex impide escribir y usar la red desde los comandos, pero **no impide leer**. Por eso cada llamada de Codex se ejecuta dentro de `codex-jail.sh`, un espacio de montaje de bubblewrap. Dentro solo existe esto:

- el sistema: `/usr`, `/etc` y `resolv.conf`;
- la instalación de Codex;
- un `CODEX_HOME` temporal para cada llamada, que solo contiene una copia de `auth.json`;
- lo que pide cada llamada: el checkout del caso, el fichero de tarea y el servidor MCP (solo lectura), y el directorio de la respuesta.

No existen `$HOME`, `/mnt`, este repo (`audit-joaquin.json`, `REVIEW-SHEET.md`, `cards/`), la revisión de Claude, los demás checkouts, `~/.codex` ni `~/.claude`.

**Prueba de acceso real antes de empezar.** Se hizo con Codex y la sesión de ChatGPT, con la configuración exacta de la ejecución (fase de revisión, MCP, jaula y un checkout real de TC4). Resultados en `access-test-output.txt`, `access-test-mcp-output.txt` y `access-test-bwrap.txt`, que es la misma prueba sin modelo, con bash dentro de la jaula:

- todas las rutas prohibidas aparecen como `absent`;
- `find /` no encuentra `audit-joaquin*`, `REVIEW-SHEET*`, `review-a.json`, `ai-comparison.json` ni `METRICS.md`;
- `curl` a raw.githubusercontent.com falla con `Could not resolve host`, así que tampoco puede leer este repo público;
- Codex no tiene búsqueda web;
- sí lee el checkout del caso;
- `find_definitions` del MCP funciona: devuelve 23 resultados.

## Ejecución (`RUN.md`)

- **Orden:** TC3, TC2, TC4. Duró desde el 2026-11-02 a las 19:17 hasta el 2026-11-03 a las 09:12 (+01:00).
- **3 paradas por límite de uso del plan:**
  1. 19:31, en TC2, con 19 de 27 hechos;
  2. 23:06, en TC4, con 53 de 160;
  3. 04:14, en TC4, con 122 de 160.
- **Reanudación:** tras cada parada se reanudó a la hora que indica Codex más 5 minutos. Los casos ya hechos se conservan y se saltan.
- **Reintento prematuro:** hubo un reintento a las 22:32, antes de que se levantara el primer límite (el `sleep` de WSL se adelantó). Se topó con el mismo límite en 4 s sin hacer ningún caso, así que no cuenta como parada nueva.
- **Respuestas:** 212 de 212 válidas; 9 casos necesitaron más de un intento.
- **Regla e:** convirtió 1 respuesta en U (TC4 P079).
- **Tokens que informa Codex:** 41,2 M de entrada (31,7 M en caché) y 0,30 M de salida.
- **Cadenas** (`verify-chains-tc*.txt`, mismo verificador `scripts/verify-chains.mjs`): **0 FAIL**. Pasan 19 en TC2, 22 en TC3 y 127 en TC4. Las demás son n/a: FP por contexto o detección, o U, que no tienen cadena que verificar.
  - El script exige `review-b.json`, que no existe en una ejecución solo con proponente. Se le pasó una copia del directorio con un `review-b.json` vacío, por eso la sección B está vacía. El script no se modificó.
- **Salidas en bruto** (`review-a.json`, `review-sheet.md`, logs): están en `~/vibe-guard-evaluation-work/calib-codex-2026-11-02/`, no en este repo. sha256 de cada `review-a.json`:
  - TC2: `04d8adaf…7578f8`
  - TC3: `26253a66…43abc2`
  - TC4: `931395025…bbca1`

## Resultado (`table-output.txt`, etiquetas v1)

| | n | Claude proponente | Codex solo | Consenso: cobertura | Consenso: acierto |
|---|---|---|---|---|---|
| TC2 (contaminado por los ejemplos) | 27 | 24/27 = 0.89 [0.72–0.96] | 24/27 = 0.89 [0.72–0.96] | 23/27 = 0.85 [0.68–0.94] | 22/23 = 0.96 [0.79–0.99] |
| TC3 | 25 | 21/25 = 0.84 [0.65–0.94] | 20/25 = 0.80 [0.61–0.91] | 23/25 = 0.92 [0.75–0.98] | 20/23 = 0.87 [0.68–0.95] |
| TC4 | 160 | 109/160 = 0.68 [0.61–0.75] | 114/160 = 0.71 [0.64–0.78] | 143/160 = 0.89 [0.84–0.93] | 105/143 = 0.73 [0.66–0.80] |
| TC3 + TC4 | 185 | 130/185 = 0.70 [0.63–0.76] | 134/185 = 0.72 [0.66–0.78] | 166/185 = 0.90 [0.85–0.93] | 125/166 = 0.75 [0.68–0.81] |
| TC2 + TC3 + TC4 | 212 | 154/212 = 0.73 [0.66–0.78] | 158/212 = 0.75 [0.68–0.80] | 189/212 = 0.89 [0.84–0.93] | 147/189 = 0.78 [0.71–0.83] |

Por idioma, en TC3 + TC4 con etiquetas v1:

| | n | Claude | Codex | Consenso: cobertura | Consenso: acierto |
|---|---|---|---|---|---|
| Java | 65 | 27/65 = 0.42 [0.30–0.54] | 29/65 = 0.45 [0.33–0.57] | 56/65 = 0.86 [0.76–0.93] | 25/56 = 0.45 [0.32–0.58] |
| Python | 120 | 103/120 = 0.86 [0.78–0.91] | 105/120 = 0.88 [0.80–0.92] | 110/120 = 0.92 [0.85–0.95] | 100/110 = 0.91 [0.84–0.95] |

`table-output.txt` contiene el resto:

- las tablas por corpus e idioma contra las etiquetas originales y las v1;
- TC2 con la re-ejecución de Claude de J001 y P116: ambos TP, igual que Codex.

Lectura, sin conclusiones más allá de los números:

- **Codex y Claude dan cifras parecidas** en todos los cortes, y sus intervalos se solapan por completo.
- **El acuerdo entre las dos IAs es alto:** 89 % de cobertura.
- **En Java, ese acuerdo no filtra errores:**
  - en TC4 Java, de 39 casos con algún fallo, 34 los fallan las dos IAs y en 31 de ellos con el mismo veredicto;
  - el acierto dentro del consenso en Java TC3 + TC4 es 0.45;
  - en Python, el consenso sube el acierto a 0.91.
- **Patrones más frecuentes cuando fallan las dos en TC4** (Joaquín → Claude/Codex):
  - FP → TP/TP: 14;
  - U → TP/TP: 12;
  - FP → U/U: 5;
  - TP → FP/FP: 4;
  - U → FP/FP: 3;
  - FP → TP/U: 3.

## Fallos (vs v1; IDs, veredictos y motivo de cada modelo en `table-output.txt`, sección "Fallos")

| Corpus | Casos con algún fallo | Solo Claude | Solo Codex | Ambos (mismo veredicto) |
|---|---|---|---|---|
| TC2 | 5: J001, J023, P073, P099, P116 | 2 (J001 y P116, inválidas en la ejecución principal) | 2 (J023 U, P099 U) | 1 (P073 FP/FP, que es un ejemplo few-shot) |
| TC3 | 5 | 0 | 1 (Java) | 4 (3) |
| TC4 | 55: 39 Java y 16 Python | 9 | 4 | 42 (38) |

Para cada fallo, `table-output.txt` da la razón completa del modelo que falla, con sus `path:line`, o el error si la respuesta fue inválida.

## Ficheros

- `codex-jail.sh`: la jaula de bubblewrap (`VIBE_GUARD_CODEX`). `JAIL_CODEX_EXEC_ARGS` añade `-c model_reasoning_effort="medium"`.
- `run.sh`: la ejecución. Si se vuelve a lanzar, reanuda. `auto-resume.sh`: espera a la hora de reinicio del límite y vuelve a lanzar `run.sh`. `RUN.md`: registro de la ejecución y de las paradas.
- `access-test.mjs`, `access-test-mcp.mjs` y `access-test-probe.sh`, con sus salidas `access-test-*.txt`: las pruebas de acceso.
- `ids-tc{2,3,4}.txt`: los IDs revisados, que son los de cada `audit-joaquin.json`.
- `table.py`: genera `table-output.txt` con `python3 table.py ~/vibe-guard-evaluation-work/calib-codex-2026-11-02 ~/vibe-guard-evaluation-work/calib-v1-2026-10-28 ~/vibe-guard-evaluation-work/tc4/ai-review ~/vibe-guard-evaluation`.
- `verify-chains-tc{2,3,4}.txt`: verificación independiente de las cadenas de Codex.
