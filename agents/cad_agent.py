TORONTO_RATES = {
    "baltic_birch_3mm_sq_inch": 0.025,  # Real yield rate with offcut waste
    "cast_acrylic_3mm_sq_inch": 0.045,  # Premium cast sheet
    "contract_laser_hourly_cad": 120.00,  # Hot Pop Factory rate
    "hardware_and_standoffs_per_unit": 35.00,  # 4x architectural standoffs + mounting template
    "shop_supplies_and_finishing": 25.00,  # 3M 467MP adhesive, Osmo hardwax-oil
}


def estimate_physical_job(brief: dict) -> dict:
  print("📊 [Agent 2: Estimator] Calculating BOM and contract cutting margins...")
  w_in = brief["target_dimensions_mm"]["width"] / 25.4
  h_in = brief["target_dimensions_mm"]["height"] / 25.4
  area_sq_in = w_in * h_in

  # Material cost for multi-layer composite plus adhesive & hardware
  mat_cost = (
      (area_sq_in * TORONTO_RATES["baltic_birch_3mm_sq_inch"])
      + (area_sq_in * TORONTO_RATES["cast_acrylic_3mm_sq_inch"])
      + TORONTO_RATES["hardware_and_standoffs_per_unit"]
      + TORONTO_RATES["shop_supplies_and_finishing"]
  )

  # Machine time: larger architectural cuts (~850x550mm) average 20-30 minutes on commercial CO2
  estimated_machine_mins = max(15.0, (area_sq_in / 30.0))
  contract_cut_cost = (
      estimated_machine_mins / 60.0
  ) * TORONTO_RATES["contract_laser_hourly_cad"]

  total_cogs = round(mat_cost + contract_cut_cost, 2)
  retail_price = brief["estimated_retail_quote_cad"]

  # Enforce minimum realistic pricing if model lowballs
  if retail_price < total_cogs * 2.5:
    retail_price = round(total_cogs * 3.0, 2)

  gross_profit = round(retail_price - total_cogs, 2)
  margin_pct = round((gross_profit / retail_price) * 100, 1)

  return {
      "dimensions_inches": f"{w_in:.1f}\" x {h_in:.1f}\"",
      "material_cost_cad": round(mat_cost, 2),
      "contract_cutting_cad": round(contract_cut_cost, 2),
      "total_cogs_cad": total_cogs,
      "proposed_retail_cad": retail_price,
      "gross_profit_cad": gross_profit,
      "gross_margin_percent": margin_pct,
  }