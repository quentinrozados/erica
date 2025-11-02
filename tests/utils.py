import os
from datetime import date

from erica.api.dto.freischaltcode import FreischaltCodeRequestDto, FreischaltCodeActivateDto, \
    FreischaltCodeRevocateDto
from erica.api.dto.tax_declaration_dto import TaxDeclarationDto
from erica.api.dto.tax_number_validation_dto import CheckTaxNumberDto
from erica.domain.payload.freischaltcode import FreischaltCodeRequestPayload, FreischaltCodeActivatePayload, \
    FreischaltCodeRevocatePayload
from erica.domain.payload.tax_declaration import TaxDeclarationPayload
from erica.domain.payload.tax_number_validation import CheckTaxNumberPayload
from erica.api.dto.grundsteuer_dto import GrundsteuerDto
from erica.api.dto.ustva_dto import (
    UstvaDto,
    UstvaPayload,
    UstvaSteuerfall,
    UstvaUnternehmer,
    UstvaUmsatzsteuervoranmeldung,
    UstvaDatenLieferant,
    UstvaHersteller,
)
from worker.samples.grundsteuer_sample_data import SampleGrundsteuerData
from worker.utils import create_meta_data, create_form_data

samples_folder = os.path.join(os.path.dirname(__file__), 'worker/samples')


def read_text_from_sample(sample_name, read_type='r'):
    with open(os.path.join(samples_folder, sample_name), read_type) as sample_xml:
        return sample_xml.read()


def create_unlock_code_request(correct=True):
    if correct:
        payload = FreischaltCodeRequestPayload(tax_id_number="04531972802", date_of_birth=date(1957, 7, 14))
    else:
        payload = FreischaltCodeRequestPayload(tax_id_number="123456789", date_of_birth=date(1969, 7, 20))

    return FreischaltCodeRequestDto(payload=payload, client_identifier="steuerlotse")


def create_unlock_code_activation(correct=True):
    if correct:
        payload = FreischaltCodeActivatePayload(tax_id_number="09952417688", freischalt_code="42",
                                                elster_request_id="CORRECT")
    else:
        payload = FreischaltCodeActivatePayload(tax_id_number="123456789", freischalt_code="INCORRECT",
                                                elster_request_id="INCORRECT")

    return FreischaltCodeActivateDto(payload=payload, client_identifier="steuerlotse")


def create_unlock_code_revocation(correct=True):
    if correct:
        payload = FreischaltCodeRevocatePayload(tax_id_number="04531972802", elster_request_id="CORRECT")
    else:
        payload = FreischaltCodeRevocatePayload(tax_id_number="123456789", elster_request_id="INCORRECT")

    return FreischaltCodeRevocateDto(payload=payload, client_identifier="steuerlotse")


def create_tax_number_validity(correct=True):
    if correct:
        payload = CheckTaxNumberPayload(state_abbreviation="BY", tax_number="04531972802")
    else:
        payload = CheckTaxNumberPayload(state_abbreviation="BY", tax_number="123456789")

    return CheckTaxNumberDto(payload=payload, client_identifier="steuerlotse")


def create_send_est():
    payload = TaxDeclarationPayload(est_data=create_form_data(), meta_data=create_meta_data())
    return TaxDeclarationDto(payload=payload, client_identifier="steuerlotse")


def create_send_grundsteuer():
    return GrundsteuerDto(payload=SampleGrundsteuerData().parse(), client_identifier="grundsteuer")


def create_send_ustva():
    payload = UstvaPayload(
        erstellungsdatum=date(2025, 1, 5),
        daten_lieferant=UstvaDatenLieferant(
            name="Alois Mustermann",
            strasse="Testgasse 13",
            plz="08151",
            ort="Musterstadt",
            telefon="0815/99999999",
            email="Mustermann@Geschaeft.de",
        ),
        steuerfall=UstvaSteuerfall(
            unternehmer=UstvaUnternehmer(
                bezeichnung="Ihr Laden",
                name="Mustermann",
                vorname="Alois",
                strasse="Testgasse",
                hausnummer="13",
                hnr_zusatz="a",
                anschriften_zusatz="Ums Eck",
                ort="Musterstadt",
                plz="08151",
                telefon="0815/99999999",
                email="Mustermann@Geschaeft.de",
            ),
            umsatzsteuervoranmeldung=UstvaUmsatzsteuervoranmeldung(
                jahr=2025,
                zeitraum="01",
                steuernummer="1096081508187",
                kz09="74931",
                kz35="10000",
                kz36="1600.00",
                kz66="15000.00",
                kz69="200.00",
                kz81="150000",
                kz83="17050.00",
                kz86="25000",
            ),
        ),
        hersteller=UstvaHersteller(
            produkt_name="Test",
            produkt_version="42",
        ),
    )
    return UstvaDto(payload=payload, client_identifier="ustva-client")


def get_job_service_patch_string(endpoint):
    return "erica.api.v2.endpoints." + endpoint + ".get_job_service"


def get_erica_request_patch_string(endpoint):
    return "erica.api.v2.endpoints." + endpoint + ".get_erica_request"
