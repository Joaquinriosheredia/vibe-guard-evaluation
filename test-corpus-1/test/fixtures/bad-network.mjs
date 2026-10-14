// Positive control: does network I/O on import.
await fetch('https://api.github.com/').catch(() => {});
