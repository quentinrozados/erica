"""Compatibility module to expose the structured UStVA payload in the domain layer."""

from erica.api.dto.ustva_dto import UstvaPayload  # re-export for legacy imports

__all__ = ["UstvaPayload"]
