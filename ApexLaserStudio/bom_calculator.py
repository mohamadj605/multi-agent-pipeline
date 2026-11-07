def calculate_bom():
    print("--- Apex Laser Designs: BOM & Quoting Calculator ---")
    print("Materials: 1=White Oak, 2=Walnut, 3=Matte Black Acrylic, 4=Clear Acrylic")
    
    mat_choice = input("Select Material (1-4): ")
    width = float(input("Enter Width (inches): "))
    height = float(input("Enter Height (inches): "))

    rates = {"1": 0.15, "2": 0.18, "3": 0.10, "4": 0.10}
    names = {"1": "White Oak", "2": "Walnut", "3": "Matte Black Acrylic", "4": "Clear Acrylic"}

    sq_inches = width * height
    material_cost = sq_inches * rates.get(mat_choice, 0.10)
    laser_time_mins = sq_inches * 2
    laser_cost = laser_time_mins * 2.00

    subtotal = material_cost + laser_cost
    total_with_markup = subtotal * 1.40

    print("\n--- Bill of Materials & Quote ---")
    print(f"Material: {names.get(mat_choice, 'Unknown')}")
    print(f"Dimensions: {width} x {height} inches ({sq_inches} sq in)")
    print(f"Material Cost: $ {material_cost:.2f}")
    print(f"Laser Time: {laser_time_mins} mins (Cost: $ {laser_cost:.2f})")
    print(f"Subtotal: $ {subtotal:.2f}")
    print(f"Final B2B Quote (40% Markup): $ {total_with_markup:.2f}")

if __name__ == "__main__":
    calculate_bom()
