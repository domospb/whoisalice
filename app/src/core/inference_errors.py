"""
Inference API error handling.

Detects outdated/unsupported models (404, model_not_supported) and raises
clear errors with links to supported model lists.
"""


def wrap_inference_error(
    exc: Exception,
    service: str,
    model: str,
    supported_url: str,
) -> None:
    """
    If the exception looks like "model not found" or "not supported",
    raise a clear ValueError. Otherwise re-raise the original.
    """
    msg = str(exc).lower()
    is_404 = "404" in msg or "not found" in msg
    is_unsupported = (
        "model_not_supported" in msg
        or "not supported" in msg
        or "not available" in msg
    )
    if is_404 or is_unsupported:
        raise ValueError(
            f"{service} model '{model}' is not available on the current inference provider. "
            f"Models change over time; use a supported model and set HF_{service}_MODEL in .env. "
            f"See: {supported_url}"
        ) from exc
    raise exc
