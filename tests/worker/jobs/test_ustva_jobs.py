import logging
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from erica.job_service.job_service import JobService
from erica.worker.jobs.ustva_jobs import send_ustva
from erica.domain.model.erica_request import RequestType


class TestUstvaJob:

    def test_perform_job_called_with_correct_parameters(self):
        request_id = "1234"

        with patch("erica.job_service.job_service_factory.get_job_service", MagicMock()) as mock_get_service, \
                patch("erica.worker.jobs.ustva_jobs.perform_job", AsyncMock()) as mock_perform_job:
            send_ustva(request_id)

            assert mock_perform_job.mock_calls == [call(request_id=request_id,
                                                        repository=mock_get_service().repository,
                                                        service=mock_get_service(),
                                                        payload_type=mock_get_service().payload_type,
                                                        logger=logging.getLogger())]

    def test_get_job_service_called_with_correct_param(self):
        request_id = "1234"

        with patch("erica.job_service.job_service_factory.get_job_service", MagicMock()) as mock_get_service, \
                patch("erica.worker.jobs.ustva_jobs.perform_job", AsyncMock()):
            send_ustva(request_id)

            assert mock_get_service.mock_calls == [call(RequestType.send_ustva)]

    @pytest.mark.usefixtures('fake_db_connection_in_settings')
    def test_request_controller_process_called_with_correct_params(self):
        request_id = "1234"
        request_payload = {
            "steuerfall": {
                "umsatzsteuervoranmeldung": {
                    "steuernummer": "1096081508187",
                    "jahr": 2025,
                    "zeitraum": "01",
                }
            }
        }
        mock_req_controller = MagicMock()
        mock_get_service = MagicMock(
            return_value=JobService(
                job_repository=MagicMock(),
                payload_type=MagicMock(parse_obj=MagicMock(return_value=request_payload)),
                request_controller=mock_req_controller,
                job_method=send_ustva
            ))
        with patch("erica.job_service.job_service_factory.get_job_service", mock_get_service), \
                patch("erica.worker.request_processing.requests_controller.UstvaRequestController", mock_req_controller):
            send_ustva(request_id)

            assert [call(request_payload, True), call().process()] in mock_req_controller.mock_calls
