# Optional Terraform example

This folder contains a minimal Terraform skeleton for deploying the container to AWS App Runner using a public ECR image.

## Requirements
- Terraform 1.5+
- AWS credentials configured locally
- A public ECR image for the service

## Example

```bash
terraform init
terraform apply \
  -var "image_identifier=public.ecr.aws/your-repo/your-image:latest" \
  -var "image_repository_type=ECR_PUBLIC"
```

For private ECR, provide access_role_arn and set image_repository_type to ECR.
