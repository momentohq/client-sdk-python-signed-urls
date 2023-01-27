from datetime import timedelta

from momento_signed_urls import SimpleCacheClientAsync


async def test_create_list_revoke_signing_keys(client_async: SimpleCacheClientAsync) -> None:
    create_resp = await client_async.create_signing_key(timedelta(minutes=30))
    list_resp = await client_async.list_signing_keys()
    assert create_resp.key_id() in [signing_key.key_id() for signing_key in list_resp.signing_keys()]

    await client_async.revoke_signing_key(create_resp.key_id())
    list_resp = await client_async.list_signing_keys()
    assert create_resp.key_id() not in [signing_key.key_id() for signing_key in list_resp.signing_keys()]
