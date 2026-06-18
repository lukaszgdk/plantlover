"""
Curated care data for common houseplants.
Keyed by lowercase species name fragments for fuzzy matching.
"""

from typing import Optional

_CARE: list[dict] = [
    # Aroids
    {"species": "monstera deliciosa", "watering_days": 7, "sunlight": "medium"},
    {"species": "monstera adansonii", "watering_days": 7, "sunlight": "medium"},
    {"species": "philodendron hederaceum", "watering_days": 7, "sunlight": "low"},
    {"species": "philodendron bipinnatifidum", "watering_days": 7, "sunlight": "medium"},
    {"species": "spathiphyllum", "watering_days": 7, "sunlight": "low"},
    {"species": "anthurium andraeanum", "watering_days": 7, "sunlight": "medium"},
    {"species": "zamioculcas zamiifolia", "watering_days": 14, "sunlight": "low"},
    {"species": "aglaonema", "watering_days": 10, "sunlight": "low"},
    {"species": "dieffenbachia", "watering_days": 7, "sunlight": "medium"},
    {"species": "alocasia", "watering_days": 7, "sunlight": "medium"},
    {"species": "colocasia", "watering_days": 5, "sunlight": "medium"},
    {"species": "caladium", "watering_days": 5, "sunlight": "medium"},
    {"species": "syngonium podophyllum", "watering_days": 7, "sunlight": "low"},
    # Epipremnum / pothos
    {"species": "epipremnum aureum", "watering_days": 7, "sunlight": "low"},
    # Ficus
    {"species": "ficus benjamina", "watering_days": 7, "sunlight": "medium"},
    {"species": "ficus elastica", "watering_days": 10, "sunlight": "medium"},
    {"species": "ficus lyrata", "watering_days": 7, "sunlight": "medium"},
    {"species": "ficus pumila", "watering_days": 5, "sunlight": "medium"},
    # Dracaena / sansevieria
    {"species": "dracaena trifasciata", "watering_days": 14, "sunlight": "low"},
    {"species": "sansevieria", "watering_days": 14, "sunlight": "low"},
    {"species": "dracaena marginata", "watering_days": 10, "sunlight": "medium"},
    {"species": "dracaena fragrans", "watering_days": 10, "sunlight": "low"},
    # Succulents & cacti
    {"species": "aloe vera", "watering_days": 14, "sunlight": "high"},
    {"species": "crassula ovata", "watering_days": 14, "sunlight": "high"},
    {"species": "haworthia", "watering_days": 14, "sunlight": "medium"},
    {"species": "echeveria", "watering_days": 14, "sunlight": "high"},
    {"species": "sedum", "watering_days": 14, "sunlight": "high"},
    {"species": "kalanchoe", "watering_days": 10, "sunlight": "high"},
    {"species": "gasteria", "watering_days": 14, "sunlight": "medium"},
    # Palms
    {"species": "chamaedorea elegans", "watering_days": 7, "sunlight": "low"},
    {"species": "howea forsteriana", "watering_days": 7, "sunlight": "medium"},
    {"species": "dypsis lutescens", "watering_days": 7, "sunlight": "medium"},
    # Chlorophytum / spider plant
    {"species": "chlorophytum comosum", "watering_days": 7, "sunlight": "medium"},
    # Peperomia
    {"species": "peperomia", "watering_days": 10, "sunlight": "medium"},
    # Calathea / maranta
    {"species": "calathea", "watering_days": 5, "sunlight": "low"},
    {"species": "maranta leuconeura", "watering_days": 5, "sunlight": "low"},
    {"species": "stromanthe", "watering_days": 5, "sunlight": "low"},
    # Potted herbs
    {"species": "ocimum basilicum", "watering_days": 3, "sunlight": "high"},
    {"species": "mentha", "watering_days": 3, "sunlight": "medium"},
    {"species": "rosmarinus officinalis", "watering_days": 7, "sunlight": "high"},
    {"species": "lavandula", "watering_days": 7, "sunlight": "high"},
    # Other popular
    {"species": "begonia", "watering_days": 5, "sunlight": "medium"},
    {"species": "impatiens", "watering_days": 3, "sunlight": "medium"},
    {"species": "cyclamen", "watering_days": 5, "sunlight": "medium"},
    {"species": "hoya", "watering_days": 10, "sunlight": "medium"},
    {"species": "scindapsus", "watering_days": 7, "sunlight": "low"},
    {"species": "tradescantia", "watering_days": 5, "sunlight": "medium"},
    {"species": "pilea peperomioides", "watering_days": 7, "sunlight": "medium"},
    {"species": "oxalis triangularis", "watering_days": 7, "sunlight": "medium"},
    {"species": "strelitzia reginae", "watering_days": 7, "sunlight": "high"},
    {"species": "clivia miniata", "watering_days": 7, "sunlight": "medium"},
    {"species": "schefflera", "watering_days": 7, "sunlight": "medium"},
    {"species": "yucca", "watering_days": 14, "sunlight": "high"},
]


def lookup(species_name: str) -> Optional[dict]:
    """Return {'watering_days': int, 'sunlight': str} or None."""
    key = species_name.lower().strip()
    for entry in _CARE:
        if entry["species"] in key or key.startswith(entry["species"].split()[0]):
            return {"watering_days": entry["watering_days"], "sunlight": entry["sunlight"]}
    return None
