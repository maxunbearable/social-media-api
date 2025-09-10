from httpx import Response
import pytest
from unittest.mock import Mock

from api.tasks import send_email

@pytest.mark.anyio
async def test_send_simple_email(mock_httpx_client):
    await send_email("test@test.com", "Test Subject", "Test Body")
    mock_httpx_client.post.assert_called()
    
@pytest.mark.anyio
async def test_send_simle_email_api_error(mock_httpx_client):
    import httpx
    response = Response(status_code=500, content="")
    response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("API Error", request=None, response=response))
    mock_httpx_client.post.return_value = response
    with pytest.raises(Exception, match="Error sending email"):
        await send_email("test@test.com", "Test Subject", "Test Body")
