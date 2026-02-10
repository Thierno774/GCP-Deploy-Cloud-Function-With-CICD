import logging
import uuid
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("order_utils")


def validate_payload(data: Dict[str, Any]) -> None:
    """
    Ensure required fields are present and types look sane.
    Raises ValueError if something is missing or malformed.
    """

    required = [
        "order_id",
        "customer_id",
        "items",
        "order_date",
        "shipping_address",
        "payment_method",
        "total_amount",
    ]

    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing fields: {missing}")

    # Items
    items = data["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("`items` must be a non-empty list")

    for i, it in enumerate(items):
        for key in ("sku", "name", "qty", "unit_price"):
            if key not in it:
                raise ValueError(f"items[{i}] missing '{key}'")

        if not isinstance(it["qty"], int) or it["qty"] <= 0:
            raise ValueError(f"items[{i}].qty must be a positive integer")

        if not isinstance(it["unit_price"], (int, float)) or it["unit_price"] <= 0:
            raise ValueError(f"items[{i}].unit_price must be a positive number")

    # Shipping address
    addr = data["shipping_address"]
    if not isinstance(addr, dict):
        raise ValueError("`shipping_address` must be an object")

    for field in ("line1", "city", "state", "postal_code", "country"):
        if field not in addr:
            raise ValueError(f"`shipping_address` missing '{field}'")

    # Payment method
    if not isinstance(data["payment_method"], str):
        raise ValueError("`payment_method` must be a string")

    # Total amount
    total_amount = data["total_amount"]
    if not isinstance(total_amount, (int, float)):
        raise ValueError("`total_amount` must be a number")

    computed = sum(it["qty"] * it["unit_price"] for it in items)
    if round(computed, 2) != round(total_amount, 2):
        raise ValueError(
            f"total_amount mismatch: expected {computed:.2f}, got {total_amount:.2f}"
        )

    logger.info("Payload validated for order %s", data["order_id"])

# Function permettant de generer des metadata 
def enrich_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add processing metadata
    """
    data["processing_id"] = uuid.uuid4().hex
    data["processed_at"] = datetime.utcnow().isoformat() + "Z"

    logger.info(
        "Payload enriched: order_id=%s processing_id=%s",
        data["order_id"],
        data["processing_id"],
    )

    return data


def simulate_db_save(data: Dict[str, Any]) -> bool:
    """
    Simulate saving the order to a database
    """
    logger.info("Simulating DB save for order %s", data["order_id"])
    return True
