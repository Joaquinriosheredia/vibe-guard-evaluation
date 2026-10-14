"""Imports one Python module (not as __main__) with network, subprocesses and file writes
intercepted; prints the intercepted calls as JSON. Used by import-is-inert.test.mjs."""
import builtins, importlib.util, json, os, shutil, socket, subprocess, sys

calls = []
def trap(obj, name, kind):
    if not hasattr(obj, name):
        return
    def blocked(*a, **k):
        calls.append(f"{kind}:{name}({str(a[0])[:80] if a else ''})")
        raise RuntimeError(f"blocked {kind}:{name}")
    setattr(obj, name, blocked)

for n in ("socket", "create_connection"):
    trap(socket, n, "network")
for n in ("run", "Popen", "call", "check_call", "check_output"):
    trap(subprocess, n, "process")
for n in ("makedirs", "mkdir", "remove", "unlink", "rename", "replace", "rmdir", "system"):
    trap(os, n, "write")
for n in ("rmtree", "copy", "copyfile", "move"):
    trap(shutil, n, "write")
real_open = builtins.open
def guarded_open(file, mode="r", *a, **k):
    if any(c in mode for c in "wax+"):
        calls.append(f"write:open({str(file)[:80]}, {mode})")
        raise RuntimeError("blocked write:open")
    return real_open(file, mode, *a, **k)
builtins.open = guarded_open
import pathlib
real_write_text = pathlib.Path.write_text
def guarded_write_text(self, *a, **k):
    calls.append(f"write:Path.write_text({str(self)[:80]})")
    raise RuntimeError("blocked write:write_text")
pathlib.Path.write_text = guarded_write_text
pathlib.Path.write_bytes = guarded_write_text

error = None
try:
    spec = importlib.util.spec_from_file_location("module_under_test", sys.argv[1])
    spec.loader.exec_module(importlib.util.module_from_spec(spec))
except BaseException as e:  # SystemExit included: a module must not exit on import either
    error = repr(e)[:300]
print(json.dumps({"calls": calls, "error": error}))
