#!/usr/bin/env python3
"""
fx_refresh_all_state.py

Wrapper that refreshes the full FX technical/state layer in staged order:
1. fx_technical_overlay.py -> Twelve Data OHLC fetch + technical overlay
2. fx_refresh_portfolio_state.py -> portfolio/state/valuation/scorecard refresh
3. tools/apply_fx_carry_accrual.py -> policy-rate proxy carry accrual into state/NAV
4. tools/write_fx_carry_and_risk_snapshots.py -> carry and true risk-bucket artifacts
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_step(script_name: str) -> None:
    script_path = ROOT / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Missing required script: {script_path}")
    print(f"STEP_START | script={script_name}", flush=True)
    subprocess.run([sys.executable, str(script_path)], check=True)
    print(f"STEP_DONE | script={script_name}", flush=True)


def main() -> None:
    run_step("fx_technical_overlay.py")
    run_step("fx_refresh_portfolio_state.py")
    run_step("tools/apply_fx_carry_accrual.py")
    run_step("tools/write_fx_carry_and_risk_snapshots.py")
    print("FX_REFRESH_ALL_OK", flush=True)


if __name__ == "__main__":
    main()
