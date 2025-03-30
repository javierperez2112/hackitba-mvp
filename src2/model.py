import numpy as np

def evaluate_carbon_investment(carbon_emissions, investment_cost, 
                              carbon_lower_limit, carbon_upper_limit,
                              cost_lower_limit, cost_upper_limit,
                              carbon_weight, cost_weight,
                              t_norm_type="algebraic", p_value=0.5):
    """
    Evaluación económica de emisiones de CO2 usando lógica difusa
    
    Parámetros:
    - carbon_emissions: Valor de emisiones de CO2 (toneladas)
    - investment_cost: Costo de inversión ($)
    - carbon_lower_limit: Límite inferior aceptable para emisiones
    - carbon_upper_limit: Límite superior aceptable para emisiones
    - cost_lower_limit: Límite inferior aceptable para costos
    - cost_upper_limit: Límite superior aceptable para costos
    - carbon_weight: Peso para emisiones de CO2 (del AHP)
    - cost_weight: Peso para costos de inversión (del AHP)
    - t_norm_type: Tipo de t-norma ("algebraic", "einstein", "hamacher_particular", "hamacher_generic")
    - p_value: Parámetro p para el producto genérico de Hamacher
    
    Retorna:
    - Valor de tp(μᵢ, μⱼ) entre 0 y 1 que representa la evaluación conjunta
    """
    # Paso 1: Calcular β para ambos objetivos
    carbon_growth = carbon_emissions > carbon_lower_limit
    beta_carbon = 1 if carbon_growth else 0
    
    cost_growth = investment_cost > cost_lower_limit
    beta_cost = 1 if cost_growth else 0
    
    # Paso 2: Calcular los estados μₘ para cada objetivo
    mu_carbon = calculate_mu(carbon_emissions, carbon_lower_limit, carbon_upper_limit, 
                            beta_carbon, carbon_weight)
    
    mu_cost = calculate_mu(investment_cost, cost_lower_limit, cost_upper_limit, 
                          beta_cost, cost_weight)
    
    # Paso 3: Calcular tp(μᵢ, μⱼ) usando la t-norma elegida
    if t_norm_type == "algebraic":
        tp_value = mu_carbon * mu_cost
    elif t_norm_type == "einstein":
        tp_value = (mu_carbon * mu_cost) / (2 - (mu_carbon + mu_cost - mu_carbon * mu_cost))
    elif t_norm_type == "hamacher_particular":
        tp_value = (mu_carbon * mu_cost) / (mu_carbon + mu_cost - mu_carbon * mu_cost)
    elif t_norm_type == "hamacher_generic":
        tp_value = (mu_carbon * mu_cost) / (p_value + (1 - p_value) * (mu_carbon + mu_cost - mu_carbon * mu_cost))
    else:
        raise ValueError("Tipo de t-norma no válido")
    
    return tp_value

def calculate_mu(value, lower_limit, upper_limit, beta, weight):
    """
    Calcula el valor μₘ según la fórmula del paso 2 del algoritmo
    """
    if upper_limit < value:
        return 0
    elif lower_limit <= value <= upper_limit:
        term1 = (upper_limit - value) / (upper_limit - lower_limit)
        term2 = (value - lower_limit) / (upper_limit - lower_limit)
        return (term1 * (1 - beta) + term2 * beta) ** weight
    else:  # value < lower_limit
        return 1 - beta
