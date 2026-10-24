// Positive control: writes a file on import.
import { writeFileSync } from 'fs';
try { writeFileSync('/tmp/should-not-exist', 'x'); } catch { /* blocked */ }
