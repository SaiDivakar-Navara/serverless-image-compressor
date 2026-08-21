import base64
import io
import json
from PIL import Image


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        file_b64 = body['file']
        quality = int(body.get('quality', 75))
        requested_format = body.get('format', 'original')

        file_bytes = base64.b64decode(file_b64)
        image = Image.open(io.BytesIO(file_bytes))

        output_format = image.format if requested_format == 'original' else requested_format.upper()
        if output_format == 'JPG':
            output_format = 'JPEG'

        # JPEG doesn't support transparency, so flatten to RGB first
        if output_format == 'JPEG' and image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        buffer = io.BytesIO()
        image.save(buffer, format=output_format, quality=quality, optimize=True)
        compressed_bytes = buffer.getvalue()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "image": base64.b64encode(compressed_bytes).decode('utf-8'),
                "format": output_format.lower(),
                "compressedSize": len(compressed_bytes)
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }