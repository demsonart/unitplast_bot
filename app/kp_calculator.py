"""
UNITGROUP KP Calculator - Real calculation logic
Supports UNITPLAST, UNIFURNITURE, UNIMETALL
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

class KPCalculator:
    """Professional calculator for quotes and estimates"""

    # ════════════════════════════════════════════════════════════════════════
    # UNITPLAST - Plastic pricing
    # ════════════════════════════════════════════════════════════════════════

    PLASTIC_MATERIALS = {
        "abs": {"name": "ABS пластик", "price_per_kg": 425, "density": 1.05},
        "pp": {"name": "PP пластик", "price_per_kg": 275, "density": 0.9},
        "pvc": {"name": "PVC пластик", "price_per_kg": 325, "density": 1.3},
        "pc": {"name": "PC пластик", "price_per_kg": 1000, "density": 1.2},
        "pe": {"name": "PE пластик", "price_per_kg": 150, "density": 0.95},
    }

    PLASTIC_LABOR_MULTIPLIER = 0.35  # 35% labor cost on top of material
    PLASTIC_MARKUP = 0.25  # 25% profit margin

    @staticmethod
    def calculate_plastic(material: str, height_mm: int, width_mm: int, depth_mm: int,
                         wall_thickness_mm: float, quantity: int) -> Dict:
        """
        Calculate plastic product price
        Formula: Volume * Density * Material Price * Labor * (1 + Markup)
        """
        if material not in KPCalculator.PLASTIC_MATERIALS:
            return {"success": False, "error": f"Unknown material: {material}"}

        mat_info = KPCalculator.PLASTIC_MATERIALS[material]

        # Calculate volume in cm³
        volume_cm3 = (height_mm * width_mm * depth_mm) / 1000

        # Calculate weight in kg
        # For hollow product, account for wall thickness
        outer_volume = volume_cm3
        inner_volume = ((height_mm - 2*wall_thickness_mm) *
                       (width_mm - 2*wall_thickness_mm) *
                       (depth_mm - 2*wall_thickness_mm)) / 1000
        actual_volume = max(outer_volume - inner_volume, outer_volume * 0.3)
        weight_kg = actual_volume * mat_info["density"]

        # Material cost
        material_cost = weight_kg * mat_info["price_per_kg"] * quantity

        # Labor cost (35% of material)
        labor_cost = material_cost * KPCalculator.PLASTIC_LABOR_MULTIPLIER

        # Subtotal before markup
        subtotal = material_cost + labor_cost

        # Markup (25%)
        markup = subtotal * KPCalculator.PLASTIC_MARKUP

        # Total
        total = subtotal + markup

        return {
            "success": True,
            "material": mat_info["name"],
            "weight_per_unit_kg": round(weight_kg, 2),
            "total_weight_kg": round(weight_kg * quantity, 2),
            "quantity": quantity,
            "material_cost": round(material_cost, 0),
            "labor_cost": round(labor_cost, 0),
            "subtotal": round(subtotal, 0),
            "markup": round(markup, 0),
            "total": round(total, 0),
            "price_per_unit": round(total / quantity, 0),
            "production_days": 5 + (quantity // 100),  # 5 days + 1 day per 100 units
            "delivery_days": 2
        }

    # ════════════════════════════════════════════════════════════════════════
    # UNIFURNITURE - Furniture pricing
    # ════════════════════════════════════════════════════════════════════════

    FURNITURE_BASE_PRICES = {
        "шкаф": {"base": 2500, "min": 1500, "max": 5000, "labor_hours": 8},
        "стол": {"base": 1750, "min": 1000, "max": 3500, "labor_hours": 6},
        "стул": {"base": 550, "min": 300, "max": 1200, "labor_hours": 2},
        "полка": {"base": 1000, "min": 500, "max": 2000, "labor_hours": 3},
        "комод": {"base": 3000, "min": 2000, "max": 5000, "labor_hours": 10},
        "кровать": {"base": 4000, "min": 3000, "max": 7000, "labor_hours": 12},
        "диван": {"base": 5000, "min": 3500, "max": 8000, "labor_hours": 14},
    }

    FURNITURE_LABOR_RATE = 500  # ₽ per hour
    FURNITURE_MATERIALS_COST = 0.40  # 40% of base is materials
    FURNITURE_MARKUP = 0.20  # 20% profit

    @staticmethod
    def calculate_furniture(furniture_type: str, length_cm: int, width_cm: int, height_cm: int,
                           material_quality: str, quantity: int) -> Dict:
        """
        Calculate furniture price
        Formula: Base * Quality Factor * Size Multiplier + Labor + Markup
        """
        furniture_type_lower = furniture_type.lower()

        if furniture_type_lower not in KPCalculator.FURNITURE_BASE_PRICES:
            return {"success": False, "error": f"Unknown furniture type: {furniture_type}"}

        base_info = KPCalculator.FURNITURE_BASE_PRICES[furniture_type_lower]
        base_price = base_info["base"]

        # Quality factor
        quality_factors = {"эконом": 0.7, "стандарт": 1.0, "премиум": 1.5, "люкс": 2.0}
        quality_factor = quality_factors.get(material_quality.lower(), 1.0)

        # Size multiplier (per 100cm³)
        size_cm3 = length_cm * width_cm * height_cm
        size_multiplier = 1.0 + (size_cm3 - 100000) / 500000

        # Price per unit
        unit_price = base_price * quality_factor * size_multiplier

        # Labor cost per unit
        labor_hours = base_info["labor_hours"]
        labor_cost_per_unit = labor_hours * KPCalculator.FURNITURE_LABOR_RATE * quality_factor

        # Total per unit before markup
        subtotal_per_unit = unit_price + labor_cost_per_unit

        # Markup
        markup_per_unit = subtotal_per_unit * KPCalculator.FURNITURE_MARKUP

        # Total per unit
        total_per_unit = subtotal_per_unit + markup_per_unit

        # Total for quantity
        total = total_per_unit * quantity

        return {
            "success": True,
            "furniture_type": furniture_type,
            "material_quality": material_quality,
            "dimensions": f"{length_cm}x{width_cm}x{height_cm} см",
            "quantity": quantity,
            "unit_price": round(unit_price, 0),
            "labor_cost_per_unit": round(labor_cost_per_unit, 0),
            "subtotal_per_unit": round(subtotal_per_unit, 0),
            "markup_per_unit": round(markup_per_unit, 0),
            "price_per_unit": round(total_per_unit, 0),
            "total": round(total, 0),
            "labor_hours_total": labor_hours * quantity,
            "production_days": 3 + (quantity // 10),
            "delivery_days": 3
        }

    # ════════════════════════════════════════════════════════════════════════
    # UNIMETALL - Metal structures pricing
    # ════════════════════════════════════════════════════════════════════════

    METAL_BASE_PRICES = {
        "рама": {"base": 1500, "weight_factor": 0.5},
        "каркас": {"base": 3000, "weight_factor": 0.8},
        "стеллаж": {"base": 2500, "weight_factor": 0.7},
        "ограда": {"base": 1200, "weight_factor": 0.6},
        "лестница": {"base": 4500, "weight_factor": 1.2},
        "навес": {"base": 3500, "weight_factor": 0.9},
    }

    METAL_PRICE_PER_KG = 150  # ₽ per kg of steel
    METAL_LABOR_RATE = 600  # ₽ per hour
    METAL_MARKUP = 0.20

    @staticmethod
    def calculate_metal(structure_type: str, width_mm: int, height_mm: int,
                       depth_mm: int, weight_kg: float, quantity: int) -> Dict:
        """
        Calculate metal structure price
        Formula: Base + (Weight * Price Per KG) + Labor + Markup
        """
        structure_type_lower = structure_type.lower()

        if structure_type_lower not in KPCalculator.METAL_BASE_PRICES:
            return {"success": False, "error": f"Unknown structure type: {structure_type}"}

        base_info = KPCalculator.METAL_BASE_PRICES[structure_type_lower]
        base_price = base_info["base"]

        # Adjust weight based on structure type
        adjusted_weight = weight_kg * base_info["weight_factor"]

        # Material cost (steel)
        material_cost = adjusted_weight * KPCalculator.METAL_PRICE_PER_KG

        # Labor cost (estimate 1 hour per 50kg)
        labor_hours = max(1, adjusted_weight / 50)
        labor_cost = labor_hours * KPCalculator.METAL_LABOR_RATE

        # Total per unit
        subtotal = base_price + material_cost + labor_cost
        markup = subtotal * KPCalculator.METAL_MARKUP
        total_per_unit = subtotal + markup

        # Total for quantity
        total = total_per_unit * quantity

        return {
            "success": True,
            "structure_type": structure_type,
            "dimensions": f"{width_mm}x{height_mm}x{depth_mm} мм",
            "weight_per_unit_kg": round(adjusted_weight, 1),
            "total_weight_kg": round(adjusted_weight * quantity, 1),
            "quantity": quantity,
            "base_price": round(base_price, 0),
            "material_cost": round(material_cost, 0),
            "labor_cost": round(labor_cost, 0),
            "subtotal": round(subtotal, 0),
            "markup": round(markup, 0),
            "price_per_unit": round(total_per_unit, 0),
            "total": round(total, 0),
            "labor_hours_total": round(labor_hours * quantity, 1),
            "production_days": 7 + (quantity // 5),
            "delivery_days": 2
        }

    # ════════════════════════════════════════════════════════════════════════
    # Universal calculator
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def calculate(material_type: str, **kwargs) -> Dict:
        """Universal calculator dispatcher"""
        material_type = material_type.lower()

        if material_type.startswith("plastic") or material_type.startswith("abs"):
            return KPCalculator.calculate_plastic(**kwargs)
        elif material_type.startswith("furniture"):
            return KPCalculator.calculate_furniture(**kwargs)
        elif material_type.startswith("metal"):
            return KPCalculator.calculate_metal(**kwargs)
        else:
            return {"success": False, "error": f"Unknown material type: {material_type}"}
