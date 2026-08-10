from app.mcp.mcp_instance import mcp

import tempfile
import subprocess
import os

# The compiler binary to use. On macOS, plain "g++" is usually aliased
# to Apple Clang, which doesn't support GCC-only headers like
# <bits/stdc++.h>. Override via the CPP_COMPILER env var if your
# Homebrew GCC version differs (e.g. "g++-15", "g++-17").
CPP_COMPILER = os.environ.get("CPP_COMPILER", "g++-16")


@mcp.tool()
def execute_cpp(code: str, stdin: str = "") -> dict:
    """
    Compiles and executes C++ code.

    Returns:
        {
            "compiled": bool,
            "stdout": str,
            "stderr": str,
            "exit_code": int
        }
    """

    with tempfile.TemporaryDirectory() as temp_dir:

        cpp_file = os.path.join(temp_dir, "main.cpp")
        executable = os.path.join(temp_dir, "main")

        # Save source code
        with open(cpp_file, "w") as f:
            f.write(code)

        # Compile
        compile_process = subprocess.run(
            [
                CPP_COMPILER,
                cpp_file,
                "-std=c++17",
                "-o",
                executable,
            ],
            capture_output=True,
            text=True,
        )

        if compile_process.returncode != 0:
            return {
                "compiled": False,
                "stdout": "",
                "stderr": compile_process.stderr,
                "exit_code": compile_process.returncode,
            }

        # Run executable
        run_process = subprocess.run(
            [executable],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=5,
        )

        return {
            "compiled": True,
            "stdout": run_process.stdout,
            "stderr": run_process.stderr,
            "exit_code": run_process.returncode,
        }