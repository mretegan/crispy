"""Entry point of the frozen application.

In the frozen application ``sys.executable`` is Crispy, not Python. Crispy starts
Jupyter Lab with ``sys.executable -m jupyterlab``, and Jupyter starts kernels with
``sys.executable -m ipykernel_launcher``. This script runs these commands as
``python -m <module>`` does, and otherwise starts the GUI.

The check must come before the GUI imports: silx sets the Qt backend of
matplotlib on import, and the kernel would then not use the inline backend.
"""

import os
import runpy
import sys

# The PyInstaller hook of matplotlib sets MPLCONFIGDIR to a new temporary folder
# at each start, and matplotlib then builds its font cache again. Use a
# persistent folder instead.
if sys.platform == "darwin":
    cachePath = os.path.expanduser(os.path.join("~", "Library", "Caches"))
else:
    cachePath = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
os.environ["MPLCONFIGDIR"] = os.path.join(cachePath, "Crispy", "matplotlib")

if len(sys.argv) > 2 and sys.argv[1] == "-m":
    # A windowed application on Windows has no standard streams, but Jupyter
    # writes its log to them.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")  # noqa: SIM115
    # Use the bundled "python3" kernel, not a "python3" kernel of the user.
    os.environ["JUPYTER_PREFER_ENV_PATH"] = "1"
    module = sys.argv[2]
    del sys.argv[1:3]
    runpy.run_module(module, run_name="__main__", alter_sys=True)
else:
    from crispy.__main__ import main

    main()
