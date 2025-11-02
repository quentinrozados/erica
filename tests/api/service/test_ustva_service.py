import uuid
from unittest.mock import MagicMock

import pytest

from erica.api.dto.response_dto import JobState
from erica.api.service.ustva_service import UstvaService
from erica.domain.model.erica_request import EricaRequest, RequestType, Status


class TestUstvaService:

    @pytest.mark.parametrize("status", [Status.new, Status.scheduled, Status.processing])
    def test_if_erica_request_not_finished_then_return_processing_response(self, status):
        erica_request = EricaRequest(type=RequestType.send_ustva, status=status,
                                     payload={},
                                     request_id=uuid.uuid4(),
                                     creator_id="test")
        mock_get_request_by_request_id = MagicMock(return_value=erica_request)
        mock_service = MagicMock(get_request_by_request_id=mock_get_request_by_request_id)
        response = UstvaService(service=mock_service).get_response_send_ustva("test")
        assert response.process_status == JobState.PROCESSING
        assert response.result is None
        assert response.error_code is None
        assert response.error_message is None

    def test_if_erica_request_failed_then_return_failure_response(self):
        error_code = "1"
        error_message = "wingardium leviosa"
        erica_request = EricaRequest(type=RequestType.send_ustva, status=Status.failed,
                                     payload={},
                                     error_code=error_code,
                                     error_message=error_message,
                                     request_id=uuid.uuid4(),
                                     creator_id="test")
        mock_get_request_by_request_id = MagicMock(return_value=erica_request)
        mock_service = MagicMock(get_request_by_request_id=mock_get_request_by_request_id)
        response = UstvaService(service=mock_service).get_response_send_ustva("test")
        assert response.process_status == JobState.FAILURE
        assert response.error_code == error_code
        assert response.error_message == error_message
        assert response.result is None

    def test_if_erica_request_success_then_return_success_response(self):
        transferticket = "TICKET-123"
        erica_request = EricaRequest(type=RequestType.send_ustva, status=Status.success,
                                     payload={},
                                     result={"transferticket": transferticket},
                                     request_id=uuid.uuid4(),
                                     creator_id="test")
        mock_get_request_by_request_id = MagicMock(return_value=erica_request)
        mock_service = MagicMock(get_request_by_request_id=mock_get_request_by_request_id)
        response = UstvaService(service=mock_service).get_response_send_ustva("test")
        assert response.process_status == JobState.SUCCESS
        assert response.result.transferticket == transferticket
        assert response.error_code is None
        assert response.error_message is None
