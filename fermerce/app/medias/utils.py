from io import BytesIO
import typing as t
from fastapi import UploadFile
from PIL import Image
import ffmpeg
import mimetypes


async def compress_file(file: UploadFile, max_size: int = 200) -> t.Tuple[bytes, str]:
    # Read the file contents
    contents = await file.read()

    # Get the file type
    file_type = mimetypes.guess_type(file.filename)[0]

    # Compress the file based on its type
    if file_type and file_type.startswith("image"):
        # Open the image
        image = Image.open(BytesIO(contents))

        # Compress the image
        while True:
            # Save the image with the desired quality
            buffer = BytesIO()
            image.save(buffer, format="WEBP", optimize=True, quality=70)
            buffer.seek(0)

            # Check the file size of the compressed image
            size = len(buffer.getvalue()) / 1024
            if size < max_size:
                break

            # Decrease the quality and try again
            image = image.resize(
                (int(image.size[0] * 0.9), int(image.size[1] * 0.9)), Image.ANTIALIAS
            )

        # Return the compressed image
        content_type = "image/webp"
        return buffer.getvalue(), content_type
    elif file_type and file_type.startswith("video"):
        # Set the video bitrate
        bitrate = "500k"

        # Compress the video
        process = (
            ffmpeg.FFmpeg()
            .option("y")
            .input("pipe:", format="h264")
            .output(
                "tem.mp4",
                {
                    "codec:v": "libx264",
                    "b:v": bitrate,
                },
                vf="scale=420:-1",
                preset="medium",
                crf=23,
                acodec="copy",
            )
        )
        out = process.execute(stream=contents)

        # Return the compressed video
        return out, "video/mp4"
    else:
        # Unsupported file type
        raise ValueError("Unsupported file type")


def iter_media(file_obj: bytes, chunk_size) -> object:
    with open(file_obj, mode="rb", buffering=chunk_size) as file_obj:
        yield from file_obj
