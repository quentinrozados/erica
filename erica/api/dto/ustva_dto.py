from datetime import date
from typing import Optional

from erica.api.dto.base_dto import BaseDto
from erica.api.dto.response_dto import ResponseBaseDto, ResultTransferTicketResponseDto
from erica.domain.model.base_domain_model import BasePayload


class UstvaBaseModel(BaseDto):
    class Config(BaseDto.Config):
        extra = "allow"


class UstvaHersteller(UstvaBaseModel):
    produkt_name: str
    produkt_version: str


class UstvaDatenLieferant(UstvaBaseModel):
    name: Optional[str]
    strasse: Optional[str]
    plz: Optional[str]
    ort: Optional[str]
    telefon: Optional[str]
    email: Optional[str]


class UstvaBerater(UstvaBaseModel):
    bezeichnung: Optional[str]
    name: Optional[str]
    vorname: Optional[str]
    namensvorsatz: Optional[str]
    namenszusatz: Optional[str]
    strasse: Optional[str]
    hausnummer: Optional[str]
    hnr_zusatz: Optional[str]
    anschriften_zusatz: Optional[str]
    ort: Optional[str]
    plz: Optional[str]
    auslands_plz: Optional[str]
    land: Optional[str]
    postfach_ort: Optional[str]
    postfach: Optional[str]
    postfach_plz: Optional[str]
    gk_plz: Optional[str]
    telefon: Optional[str]
    email: Optional[str]


class UstvaMandant(UstvaBaseModel):
    name: Optional[str]
    vorname: Optional[str]
    mandanten_nr: Optional[str]
    bearbeiterkennzeichen: Optional[str]


class UstvaUnternehmer(UstvaBerater):
    pass


class UstvaUmsatzsteuervoranmeldung(UstvaBaseModel):
    jahr: Optional[int]
    zeitraum: Optional[str]
    steuernummer: Optional[str]
    w_id_nr: Optional[str]


class UstvaDauerfristverlaengerung(UstvaBaseModel):
    jahr: Optional[int]
    steuernummer: Optional[str]
    w_id_nr: Optional[str]


class UstvaUmsatzsteuersondervorauszahlung(UstvaBaseModel):
    jahr: Optional[int]
    steuernummer: Optional[str]
    w_id_nr: Optional[str]


class UstvaEOP(UstvaBaseModel):
    transferaufgabe: Optional[str]


class UstvaSteuerfall(UstvaBaseModel):
    berater: Optional[UstvaBerater]
    mandant: Optional[UstvaMandant]
    unternehmer: Optional[UstvaUnternehmer]
    umsatzsteuervoranmeldung: Optional[UstvaUmsatzsteuervoranmeldung]
    dauerfristverlaengerung: Optional[UstvaDauerfristverlaengerung]
    umsatzsteuersondervorauszahlung: Optional[UstvaUmsatzsteuersondervorauszahlung]


class UstvaPayload(BasePayload, UstvaBaseModel):
    erstellungsdatum: Optional[date]
    daten_lieferant: Optional[UstvaDatenLieferant]
    steuerfall: UstvaSteuerfall
    eop: Optional[UstvaEOP]
    hersteller: Optional[UstvaHersteller]
    nutzdaten_ticket: str = "1"
    nutzdaten_header_version: str = "11"
    empfaenger: Optional[str]
    use_testmerker: Optional[bool]


class UstvaDto(BaseDto):
    payload: UstvaPayload
    client_identifier: str


class UstvaResponseDto(ResponseBaseDto):
    result: Optional[ResultTransferTicketResponseDto]
