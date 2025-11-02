import xml.etree.ElementTree as ET
from datetime import date

from erica.api.dto.ustva_dto import (
    UstvaPayload,
    UstvaSteuerfall,
    UstvaUnternehmer,
    UstvaUmsatzsteuervoranmeldung,
    UstvaDatenLieferant,
    UstvaHersteller,
)
from erica.worker.elster_xml.ustva_xml import build_ustva_xml, ELSTER_NS, USTVA_NS


def _sample_payload() -> UstvaPayload:
    return UstvaPayload(
        erstellungsdatum=date(2025, 1, 5),
        daten_lieferant=UstvaDatenLieferant(
            name="Alois Mustermann",
            strasse="Testgasse 13",
            plz="08151",
            ort="Musterstadt",
        ),
        steuerfall=UstvaSteuerfall(
            unternehmer=UstvaUnternehmer(
                bezeichnung="Ihr Laden",
                name="Mustermann",
                vorname="Alois",
                strasse="Testgasse",
                hausnummer="13",
                ort="Musterstadt",
                plz="08151",
            ),
            umsatzsteuervoranmeldung=UstvaUmsatzsteuervoranmeldung(
                jahr=2025,
                zeitraum="01",
                steuernummer="1096081508187",
                kz35="10000",
                kz36="1600.00",
            ),
        ),
        hersteller=UstvaHersteller(
            produkt_name="Test",
            produkt_version="42",
        ),
    )


def test_build_ustva_xml_contains_expected_elements():
    payload = _sample_payload()
    xml_string = build_ustva_xml(payload)

    root = ET.fromstring(xml_string)
    ns = {"elster": ELSTER_NS, "ustva": USTVA_NS}

    empfaenger = root.find('.//elster:Empfaenger', ns)
    assert empfaenger is not None
    assert empfaenger.text == '1096'

    jahr = root.find('.//ustva:Umsatzsteuervoranmeldung/ustva:Jahr', ns)
    assert jahr is not None
    assert jahr.text == '2025'

    kz35 = root.find('.//ustva:Umsatzsteuervoranmeldung/ustva:Kz35', ns)
    assert kz35 is not None
    assert kz35.text == '10000'

    produkt_name = root.find('.//elster:Hersteller/elster:ProduktName', ns)
    assert produkt_name is not None
    assert produkt_name.text == 'Test'
