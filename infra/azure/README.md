# Triển khai Azure cho AI Service

Template `main.bicep` tạo Azure Container Apps Environment, Log Analytics và
AI Service với HTTPS ingress, health probes, autoscaling và managed identity.
Template không lưu khóa API hay mật khẩu. Mọi bí mật phải được tạo trong Azure
Key Vault/Container Apps secrets bởi người quản trị triển khai.

Workflow `.github/workflows/ai-service-deploy.yml` dùng Azure OIDC, một GitHub
Environment được bảo vệ và image bất biến do người triển khai cung cấp. Trước
khi chạy, cấu hình sáu GitHub Environment variables: `AZURE_CLIENT_ID`,
`AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`,
`AZURE_CONTAINER_REGISTRY_SERVER` và `AZURE_REGISTRY_PULL_IDENTITY_ID`.
Identity registry phải tồn tại trước và có role `AcrPull` trên ACR.

Ingress mặc định là nội bộ vì prototype không tự xác thực người dùng. Backend
hoặc API gateway trong mạng được phép mới gọi AI Service. Vì GitHub-hosted runner
không truy cập endpoint nội bộ, smoke test sau deployment phải chạy từ runner/job
có kết nối tới cùng mạng; workflow CI vẫn chạy smoke test đầy đủ trên container.

Kiểm tra template:

```bash
az bicep build --file infra/azure/main.bicep
```

Triển khai thử nghiệm sau khi image đã được đẩy lên registry:

```bash
az deployment group create \
  --resource-group <resource-group> \
  --template-file infra/azure/main.bicep \
  --parameters environmentName=dev \
               containerImage=<registry/image@digest> \
               registryServer=<registry.azurecr.io> \
               registryPullIdentityResourceId=<managed-identity-resource-id>
```

Sau khi smoke test thành công, dùng Container Apps revision weights để chuyển
lưu lượng dần sang revision mới. Nếu có lỗi, chuyển 100% lưu lượng về revision
trước đó; không xóa revision cũ trước khi hết thời gian quan sát.
