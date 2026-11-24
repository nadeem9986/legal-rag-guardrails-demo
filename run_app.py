"""Run one version's real Streamlit app with the free local backend:
     streamlit run run_app.py -- before      (or: after)
"""
import os
import runpy
import sys

which = sys.argv[-1] if sys.argv[-1] in ("before", "after") else "after"
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import local_backend
local_backend.install(os.path.join(here, which))
runpy.run_path(os.path.join(here, which, "app.py"), run_name="__main__")
