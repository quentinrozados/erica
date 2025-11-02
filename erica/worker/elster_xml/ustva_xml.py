"""Utilities to build the UStVA XML structure for the 2025 schema."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, Optional, Union
import xml.etree.ElementTree as ET

from pydantic import BaseModel

from erica.api.dto.ustva_dto import (
    UstvaPayload,
    UstvaSteuerfall,
)
from erica.worker.elster_xml.common.transfer_header import add_transfer_header
from erica.worker.elster_xml.transfer_header_fields import get_ustva_th_fields

ELSTER_NS = "http://www.elster.de/elsterxml/schema/v11"
USTVA_NS = "http://finkonsens.de/elster/elsteranmeldung/ustva/v2025"

DATEN_LIEFERANT_MAPPING = {
    "name": "Name",
    "strasse": "Strasse",
    "plz": "PLZ",
    "ort": "Ort",
    "telefon": "Telefon",
    "email": "Email",
}

PARTY_MAPPING = {
    "bezeichnung": "Bezeichnung",
    "name": "Name",
    "vorname": "Vorname",
    "namensvorsatz": "Namensvorsatz",
    "namenszusatz": "Namenszusatz",
    "strasse": "Str",
    "hausnummer": "Hausnummer",
    "hnr_zusatz": "HNrZusatz",
    "anschriften_zusatz": "AnschriftenZusatz",
    "ort": "Ort",
    "plz": "PLZ",
    "auslands_plz": "AuslandsPLZ",
    "land": "Land",
    "postfach_ort": "PostfachOrt",
    "postfach": "Postfach",
    "postfach_plz": "PostfachPLZ",
    "gk_plz": "GKPLZ",
    "telefon": "Telefon",
    "email": "Email",
}

MANDANT_MAPPING = {
    "name": "Name",
    "vorname": "Vorname",
    "mandanten_nr": "MandantenNr",
    "bearbeiterkennzeichen": "Bearbeiterkennzeichen",
}

UMSATZSTEUER_MAPPING = {
    "jahr": "Jahr",
    "zeitraum": "Zeitraum",
    "steuernummer": "Steuernummer",
    "w_id_nr": "WIdNr",
}

DAUERFRIST_MAPPING = {
    "jahr": "Jahr",
    "steuernummer": "Steuernummer",
    "w_id_nr": "WIdNr",
}

SONDERVORAUSZAHLUNG_MAPPING = {
    "jahr": "Jahr",
    "steuernummer": "Steuernummer",
    "w_id_nr": "WIdNr",
}

EOP_MAPPING = {"transferaufgabe": "Transferaufgabe"}


def generate_full_ustva_xml(payload: UstvaPayload, use_testmerker: bool) -> str:
    """Construct the full UStVA XML and enrich it with a transfer header."""
    xml_without_th = build_ustva_xml(payload)
    return add_transfer_header(xml_without_th, get_ustva_th_fields(use_testmerker))


def build_ustva_xml(payload: UstvaPayload) -> str:
    """Build the UStVA XML structure without a transfer header."""
    root = ET.Element("Elster", {"xmlns": ELSTER_NS})

    daten_teil = ET.SubElement(root, "DatenTeil")
    nutzdaten_block = ET.SubElement(daten_teil, "Nutzdatenblock")

    header_version = payload.nutzdaten_header_version or "11"
    nutzdaten_header = ET.SubElement(nutzdaten_block, "NutzdatenHeader", {"version": header_version})
    ET.SubElement(nutzdaten_header, "NutzdatenTicket").text = payload.nutzdaten_ticket or "1"

    empfaenger_text = _derive_empfaenger(payload)
    ET.SubElement(nutzdaten_header, "Empfaenger", {"id": "F"}).text = empfaenger_text

    if payload.hersteller:
        hersteller_data = _prepare_dict(payload.hersteller)
        hersteller_elem = ET.SubElement(nutzdaten_header, "Hersteller")
        _serialize_section(hersteller_elem, hersteller_data, {})

    nutzdaten = ET.SubElement(nutzdaten_block, "Nutzdaten")
    anmeldungssteuern = ET.SubElement(
        nutzdaten,
        "Anmeldungssteuern",
        {"xmlns": USTVA_NS, "version": "2025"},
    )

    if payload.erstellungsdatum:
        ET.SubElement(anmeldungssteuern, "Erstellungsdatum").text = _format_date(payload.erstellungsdatum)

    if payload.daten_lieferant:
        daten_lieferant_elem = ET.SubElement(anmeldungssteuern, "DatenLieferant")
        daten_lieferant_data = _prepare_dict(payload.daten_lieferant)
        _serialize_section(daten_lieferant_elem, daten_lieferant_data, DATEN_LIEFERANT_MAPPING)

    if payload.steuerfall:
        steuerfall_elem = ET.SubElement(anmeldungssteuern, "Steuerfall")
        _serialize_steuerfall(steuerfall_elem, payload.steuerfall)

    if payload.eop:
        eop_elem = ET.SubElement(anmeldungssteuern, "EOP")
        eop_data = _prepare_dict(payload.eop)
        _serialize_section(eop_elem, eop_data, EOP_MAPPING)

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")


def _serialize_steuerfall(parent: ET.Element, steuerfall: UstvaSteuerfall) -> None:
    data = _prepare_dict(steuerfall)

    def _pop(name: str) -> Any:
        return data.pop(name, None)

    berater_data = _pop("berater")
    if berater_data:
        berater_elem = ET.SubElement(parent, "Berater")
        _serialize_section(berater_elem, berater_data, PARTY_MAPPING)

    mandant_data = _pop("mandant")
    if mandant_data:
        mandant_elem = ET.SubElement(parent, "Mandant")
        _serialize_section(mandant_elem, mandant_data, MANDANT_MAPPING)

    unternehmer_data = _pop("unternehmer")
    if unternehmer_data:
        unternehmer_elem = ET.SubElement(parent, "Unternehmer")
        _serialize_section(unternehmer_elem, unternehmer_data, PARTY_MAPPING)

    voranmeldung_data = _pop("umsatzsteuervoranmeldung")
    if voranmeldung_data:
        vor_elem = ET.SubElement(parent, "Umsatzsteuervoranmeldung")
        _serialize_section(vor_elem, voranmeldung_data, UMSATZSTEUER_MAPPING)

    dauerfrist_data = _pop("dauerfristverlaengerung")
    if dauerfrist_data:
        dauer_elem = ET.SubElement(parent, "Dauerfristverlaengerung")
        _serialize_section(dauer_elem, dauerfrist_data, DAUERFRIST_MAPPING)

    sonder_data = _pop("umsatzsteuersondervorauszahlung")
    if sonder_data:
        sonder_elem = ET.SubElement(parent, "Umsatzsteuersondervorauszahlung")
        _serialize_section(sonder_elem, sonder_data, SONDERVORAUSZAHLUNG_MAPPING)

    for key, value in data.items():
        if value is None:
            continue
        child = ET.SubElement(parent, _default_transform(key))
        _append_value(child, value)


def _serialize_section(parent: ET.Element, data: Dict[str, Any], mapping: Dict[str, str]) -> None:
    processed_keys = set()

    for key in mapping:
        if key not in data:
            continue
        value = data[key]
        processed_keys.add(key)
        if value is None:
            continue
        child_tag = mapping[key]
        _append_child(parent, child_tag, value)

    for key, value in data.items():
        if key in processed_keys or value is None:
            continue
        child_tag = mapping.get(key, _default_transform(key))
        _append_child(parent, child_tag, value)


def _append_child(parent: ET.Element, tag: str, value: Any) -> None:
    if isinstance(value, (list, tuple, set)):
        for item in value:
            if item is None:
                continue
            _append_child(parent, tag, item)
        return

    if isinstance(value, (BaseModel, dict)):
        child = ET.SubElement(parent, tag)
        nested = _prepare_dict(value)
        _serialize_section(child, nested, {})
        return

    child = ET.SubElement(parent, tag)
    child.text = _format_value(value)


def _append_value(parent: ET.Element, value: Any) -> None:
    if isinstance(value, (BaseModel, dict)):
        nested = _prepare_dict(value)
        _serialize_section(parent, nested, {})
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            if item is None:
                continue
            elem = ET.SubElement(parent, "Item")
            _append_value(elem, item)
    else:
        parent.text = _format_value(value)


def _prepare_dict(value: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.dict(exclude_none=True)
    return dict(value)


def _derive_empfaenger(payload: UstvaPayload) -> str:
    if payload.empfaenger:
        return str(payload.empfaenger)

    steuernummer_candidates: Iterable[Optional[str]] = (
        getattr(payload.steuerfall.umsatzsteuervoranmeldung, "steuernummer", None)
        if payload.steuerfall and payload.steuerfall.umsatzsteuervoranmeldung
        else None,
        getattr(payload.steuerfall.dauerfristverlaengerung, "steuernummer", None)
        if payload.steuerfall and payload.steuerfall.dauerfristverlaengerung
        else None,
        getattr(payload.steuerfall.umsatzsteuersondervorauszahlung, "steuernummer", None)
        if payload.steuerfall and payload.steuerfall.umsatzsteuersondervorauszahlung
        else None,
    )

    for candidate in steuernummer_candidates:
        if not candidate:
            continue
        digits = "".join(ch for ch in str(candidate) if ch.isdigit())
        if len(digits) >= 4:
            return digits[:4]

    raise ValueError("Cannot derive Empfaenger without a valid Steuernummer in the payload.")


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y%m%d")
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, float):
        decimal_value = Decimal(str(value))
        return format(decimal_value, "f")
    return str(value)


def _format_date(value: Union[date, datetime, str]) -> str:
    if isinstance(value, str):
        return value
    return _format_value(value)


def _default_transform(key: str) -> str:
    if not key:
        return key
    if key[0].isupper() and "_" not in key:
        return key
    if key.isupper():
        return key
    if key.lower().startswith("kz"):
        return _transform_kz_key(key)
    parts = key.split("_")
    return "".join(part[:1].upper() + part[1:] for part in parts)


def _transform_kz_key(key: str) -> str:
    parts = key.split("_")
    first = parts[0]
    transformed_first = first[:2].capitalize() + first[2:]
    rest = [part[:1].upper() + part[1:] for part in parts[1:]]
    return "_".join([transformed_first] + rest)


__all__ = ["build_ustva_xml", "generate_full_ustva_xml"]
