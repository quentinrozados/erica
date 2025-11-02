from abc import ABCMeta, abstractmethod
from typing import Optional
from uuid import UUID

from opyoid import Module

from erica.api.dto.response_dto import JobState, ResultTransferTicketResponseDto
from erica.api.dto.ustva_dto import UstvaResponseDto
from erica.api.service.base_service import BaseService
from erica.api.service.response_state_mapper import map_status
from erica.domain.model.erica_request import RequestType


class UstvaServiceInterface(BaseService):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_response_send_ustva(self, request_id: UUID) -> UstvaResponseDto:
        pass


class UstvaService(UstvaServiceInterface):

    def get_response_send_ustva(self, request_id: UUID) -> UstvaResponseDto:
        erica_request = self.get_erica_request(request_id, RequestType.send_ustva)
        process_status = map_status(erica_request.status)
        if process_status == JobState.SUCCESS:
            result_payload: Optional[dict] = erica_request.result
            result = ResultTransferTicketResponseDto.parse_obj(result_payload) if result_payload else None
            return UstvaResponseDto(process_status=process_status, result=result)
        if process_status == JobState.FAILURE:
            return UstvaResponseDto(
                process_status=process_status,
                error_code=erica_request.error_code,
                error_message=erica_request.error_message,
                result=erica_request.result,
            )
        return UstvaResponseDto(process_status=process_status)


class UstvaServiceModule(Module):
    def configure(self) -> None:
        self.bind(UstvaServiceInterface, to_class=UstvaService)
