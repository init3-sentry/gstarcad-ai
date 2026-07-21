# demo_logic - logika kompilowana do .pyd. NIE importuje pygcad; API dostaje z loadera.
# Sluzy tylko do potwierdzenia, ze enkoder (encode-tool.ps1) dziala end-to-end.
gcutPrintf = None


def run(api):
    globals().update(api)
    gcutPrintf("\n=== demo_logic.pyd DZIALA - skompilowany kod wykonuje sie i siega API GstarCAD ===")
