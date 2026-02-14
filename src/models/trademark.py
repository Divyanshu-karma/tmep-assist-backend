# src/models/trademark.py

from typing import Dict, List


class TrademarkApplication:
    def __init__(self, data: Dict):

        self.mark = data["mark_info"]["literal"]
        self.mark_type = data["mark_info"]["type"]
        self.register = data["mark_info"]["register"]

        self.filing_basis = data["filing_basis"]["basis_type"]
        self.use_in_commerce = data["filing_basis"]["use_in_commerce"]

        self.goods_map = {
            g["class_id"]: g["description"]
            for g in data["goods_and_services"]
        }

        self.owner_name = data["owner"]["name"]
        self.owner_entity = data["owner"]["entity"]
        self.owner_citizenship = data["owner"]["citizenship"]

        self.serial_number = data["identifiers"]["serial_number"]
        self.registration_number = data["identifiers"]["registration_number"]

        self.specimen = data.get("specimen", {})
        self.disclaimer = data.get("disclaimer", {})
        self.mark_features = data.get("mark_features", {})
        self.claimed_prior_registrations = data.get("claimed_prior_registrations", [])
