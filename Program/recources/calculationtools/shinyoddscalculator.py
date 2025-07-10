def calculate_shiny_odds(base_odds=4096, rerolls=0):
    """
    Calculates shiny odds based on base odds and number of rerolls.

    :param base_odds: Base shiny odds denominator (default 4096)
    :param rerolls: Number of additional shiny checks (excluding the base check)
    :return: Probability as fraction (e.g., 1 in X)
    """
    total_rolls = 1 + rerolls
    probability = 1 - ((base_odds - 1) / base_odds) ** total_rolls
    shiny_odds = round(1 / probability)
    return shiny_odds