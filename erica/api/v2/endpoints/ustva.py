from uuid import UUID

from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from erica.api.dto.ustva_dto import UstvaDto
from erica.api.service.service_injector import get_service
from erica.api.service.ustva_service import UstvaServiceInterface
from erica.api.v2.responses.model import response_model_get_send_ustva_from_queue, response_model_post_to_queue
from erica.domain.model.erica_request import RequestType
from erica.job_service.job_service_factory import get_job_service

router = APIRouter()


@router.post('/ustva', status_code=status.HTTP_201_CREATED, responses=response_model_post_to_queue)
async def send_ustva(payload: UstvaDto, request: Request):
    """Queue a new UStVA submission."""
    result = get_job_service(RequestType.send_ustva).add_to_queue(
        payload.payload,
        payload.client_identifier,
        RequestType.send_ustva,
    )
    return RedirectResponse(
        str(request.url_for("get_send_ustva_job", request_id=str(result.request_id))).removeprefix(str(request.base_url)),
        status_code=status.HTTP_201_CREATED,
    )


@router.get('/ustva/{request_id}', status_code=status.HTTP_200_OK, responses=response_model_get_send_ustva_from_queue)
async def get_send_ustva_job(request_id: UUID):
    """Retrieve the processing status for a queued UStVA submission."""
    ustva_service: UstvaServiceInterface = get_service(RequestType.send_ustva)
    return ustva_service.get_response_send_ustva(request_id)
