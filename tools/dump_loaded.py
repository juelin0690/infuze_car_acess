import os, traceback, inspect
from pathlib import Path

out = Path("outputs")
out.mkdir(exist_ok=True)

def dump(modname: str, outname: str, logname: str):
    log = out / logname
    try:
        m = __import__(modname, fromlist=["*"])
        p = out / outname
        p.write_text(inspect.getsource(m), encoding="utf-8")
        log.write_text(f"OK\nCWD={os.getcwd()}\nMOD={modname}\nFILE={m.__file__}\nWROTE={p.resolve()}\n", encoding="utf-8")
        print("OK", modname, "->", p.resolve())
    except Exception:
        log.write_text("FAIL\n" + traceback.format_exc(), encoding="utf-8")
        print("FAIL", modname, "see", log.resolve())

dump("src.experiments", "LOADED_experiments.py", "dump_experiments.log")
dump("src.model", "LOADED_model.py", "dump_model.log")
