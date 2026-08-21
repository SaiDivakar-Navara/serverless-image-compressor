# Serverless Image Compressor

A serverless image compression tool built with AWS Lambda, API Gateway, and Terraform. Upload an image through a browser-based frontend, and it's compressed on the fly using Python's Pillow library — no servers to manage, no images stored.

## Architecture


efasfqer

The image is sent as base64-encoded JSON, compressed in-memory by Lambda, and the compressed result is returned directly in the same HTTP response — fully synchronous, no polling or storage step required.

## Tech stack

- **AWS Lambda** (Python 3.12) — compression logic using Pillow
- **Amazon API Gateway** (REST API) — HTTP endpoint with CORS support
- **AWS Lambda Layers** — Pillow dependency via [Klayers](https://github.com/keithrozario/Klayers)
- **IAM** — least-privilege execution role
- **Amazon CloudWatch** — execution logging
- **Terraform** — full infrastructure as code
- **HTML/CSS/JavaScript** — vanilla frontend, no frameworks or build step

## Features

- Adjustable compression quality (10–95)
- Output format conversion: original, JPEG, WebP, PNG
- Drag-and-drop upload with live preview
- Before/after file size comparison
- Fully serverless — pay only for compute time used

## Project structure

```
.
├── main.tf              # All AWS infrastructure resources
├── provider.tf           # AWS + Klayers provider configuration
├── lambda/
│   └── index.py          # Lambda function (compression logic)
├── index.html             # Frontend UI
└── README.md
```

## Setup

### Prerequisites

- An AWS account with credentials configured (`aws configure`)
- [Terraform](https://developer.hashicorp.com/terraform/install) installed
- Python 3.12 (for local testing, optional)

### Deploy

1. **Zip the Lambda function.** `index.py` must sit at the root of the zip:
   ```bash
   cd lambda
   zip ../lambda.zip index.py
   cd ..
   ```
   (On Windows, use `Compress-Archive -Path index.py -DestinationPath ..\lambda.zip -Force` from inside the `lambda` folder.)

2. **Initialize and deploy:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. **Copy the `api_url` output** and paste it into `index.html`:
   ```javascript
   const API_ENDPOINT = "https://your-api-id.execute-api.your-region.amazonaws.com/mystage/resource";
   ```

4. **Open `index.html`** in your browser and test with an image.

### Teardown

```bash
terraform destroy
```

## What I learned building this

- **Lambda handler paths must exactly match the zip's internal structure** — a mismatch here fails silently as an import error, not an obvious config error.
- **API Gateway REST API deployments are a snapshot in time.** Adding new resources (like CORS/OPTIONS support) after an initial deployment requires explicit `depends_on` and `triggers` on the `aws_api_gateway_deployment` resource, or the new config silently never goes live.
- **CORS errors in the browser console are often a red herring.** A Lambda crash (missing handler, timeout) returns a generic error response without CORS headers — the browser reports this as a CORS failure even though the real issue is upstream. CloudWatch Logs are the reliable source of truth, not browser console messages.
- **Lambda's default timeout (3 seconds) is often too short** for cold starts involving a Lambda Layer plus real compute work like image compression. Bumped to 30s timeout / 256MB memory.
- **Pillow requires Linux-compiled binaries** to run on Lambda — a locally `pip install`-ed version (on Windows/Mac) won't work. Used a prebuilt public Lambda layer (Klayers) instead of building one manually with Docker.

## Possible next steps

- Switch to presigned S3 URLs for direct browser-to-S3 uploads (removes API Gateway's 10MB payload limit)
- Add S3 storage for compressed output with expiring download links
- CI/CD pipeline for automatic `terraform apply` on push
- Multi-region deployment
