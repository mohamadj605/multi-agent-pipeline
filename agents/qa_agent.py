def audit_commercial_job(brief: dict, financials: dict) -> dict:
    print("📐 [Agent 3: Production Auditor] Verifying project tolerances and margin gates...")
    errors = []
    warnings = []

    # Check commercial bed limits (Hot Pop Factory 900x600mm or xTool D1 Pro Extended 930x430mm)
    w = brief["target_dimensions_mm"]["width"]
    h = brief["target_dimensions_mm"]["height"]
    if w > 900 or h > 600:
        errors.append(f"Dimensions ({w}x{h}mm) exceed standard commercial sheet bed (900x600mm).")

    # Financial Margin Gate: B2B physical fabrication should never drop below 55% gross margin
    if financials["gross_margin_percent"] < 55.0:
        warnings.append(f"Gross margin ({financials['gross_margin_percent']}%) is below target 55%. Raise retail pricing.")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "specs_verified": f"{w}mm x {h}mm on {', '.join(brief['substrate_stack'])}"
    }