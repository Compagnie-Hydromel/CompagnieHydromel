from fastapi import HTTPException
from starlette.formparsers import MultiPartException, MultiPartParser


class UploadTooLarge(MultiPartException):
    pass


async def image_upload_form(request, max_bytes, max_fields):
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        raise HTTPException(
            status_code=415, detail="Upload an image using multipart/form-data")

    async def bounded_stream():
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > max_bytes + 65536:
                raise UploadTooLarge("Upload exceeds 8 MiB")
            yield chunk

    try:
        return await MultiPartParser(request.headers, bounded_stream(), max_files=1,
                                     max_fields=max_fields, max_part_size=4096).parse()
    except UploadTooLarge:
        raise HTTPException(status_code=413, detail="Image exceeds 8 MiB")
    except MultiPartException:
        raise HTTPException(status_code=400, detail="Invalid image upload")
