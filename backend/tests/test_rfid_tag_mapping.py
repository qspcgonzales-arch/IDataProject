"""
Model-level unit tests for rfid.tag.mapping.

Covers: unique EPC constraint, required product_id, optional lot_id
(must never be required — this is the deciding factor behind
rfid.tag.mapping over Barcode Nomenclature per Section 2 of the
Rev. 2 roadmap), and the three encoding_type scenarios.
"""

import pytest
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


@pytest.mark.integration
class TestRfidTagMapping:

    def test_create_minimal_mapping(self, env, sample_products):
        """A mapping only needs an epc and a product_id."""
        product = sample_products[0]
        mapping = env["rfid.tag.mapping"].create(
            {
                "epc": "E28011700000021500000001",
                "product_id": product.id,
                "encoding_type": "in_house",
            }
        )
        assert mapping.lot_id.id is False
        assert mapping.encoding_type == "in_house"

    def test_epc_unique_constraint(self, env, sample_products):
        """Two mappings cannot share the same EPC."""
        product = sample_products[0]
        epc = "E28011700000021500000002"
        env["rfid.tag.mapping"].create(
            {"epc": epc, "product_id": product.id, "encoding_type": "in_house"}
        )
        with mute_logger("odoo.sql_db"), pytest.raises(Exception):
            env["rfid.tag.mapping"].create(
                {"epc": epc, "product_id": product.id, "encoding_type": "in_house"}
            )

    def test_lot_id_never_required(self, env, sample_products):
        """An unmapped/blank lot_id must never block mapping creation —
        this is the core reason rfid.tag.mapping exists instead of
        relying on Barcode Nomenclature."""
        product = sample_products[1]
        mapping = env["rfid.tag.mapping"].create(
            {
                "epc": "E28011700000021500000003",
                "product_id": product.id,
                "encoding_type": "non_standard",
                "serial_number": "SN-NONSTD-001",
            }
        )
        assert mapping.lot_id.id is False
        assert mapping.serial_number == "SN-NONSTD-001"

    def test_supplier_encoding_scenario(self, env, sample_products):
        """Scenario 1: supplier pre-encoded — resolves via barcode."""
        product = sample_products[2]
        mapping = env["rfid.tag.mapping"].create(
            {
                "epc": "E28011700000021500000004",
                "product_id": product.id,
                "encoding_type": "supplier",
                "barcode": product.barcode,
            }
        )
        assert mapping.encoding_type == "supplier"
        assert mapping.barcode == product.barcode

    def test_product_id_required(self, env):
        """product_id is mandatory even when other fields are set."""
        with pytest.raises(Exception):
            env["rfid.tag.mapping"].create(
                {"epc": "E28011700000021500000005", "encoding_type": "in_house"}
            )
