# TODO

This file tracks the remaining tasks for the Sol-Calc project.

## SECRETS MANAGEMENT

### Vault Configuration

1.  **Enable AppRole Auth Method:**
    ```bash
    vault auth enable approle
    ```

2.  **Create a Policy for the Application:**
    ```bash
    vault policy write sol-calc-app - <<EOF
    path "secret/data/sol-calc/database" {
      capabilities = ["read"]
    }
    path "secret/data/sol-calc/stripe" {
      capabilities = ["read"]
    }
    EOF
    ```

3.  **Create the AppRole:**
    ```bash
    vault write auth/approle/role/sol-calc-app \
        secret_id_ttl=10m \
        token_num_uses=10 \
        token_ttl=20m \
        token_max_ttl=30m \
        secret_id_num_uses=40 \
        policies="sol-calc-app"
    ```

4.  **Get the RoleID:**
    ```bash
    vault read auth/approle/role/sol-calc-app/role-id
    ```

5.  **Get a SecretID:**
    ```bash
    vault write -f auth/approle/role/sol-calc-app/secret-id
    ```

6.  **Create the Secrets:**
    ```bash
    vault kv put secret/sol-calc/database \
        POSTGRES_DB=solcalc \
        POSTGRES_USER=user \
        POSTGRES_PASSWORD=password

    vault kv put secret/sol-calc/stripe \
        STRIPE_API_KEY=your_stripe_api_key
    ```

## COOLIFY DEPLOYMENT

1.  **Update `docker-compose.yml`:**
    *   Add Vault Agent sidecar containers to the `payment-service` and `db` services.
    *   Add a shared volume for the secrets.
    *   Configure the application services to source the secrets from the shared volume.

2.  **Provide Deployment Instructions:**
    *   Document the required environment variables for deployment (`VAULT_ADDR`, `VAULT_ROLE_ID`, `VAULT_SECRET_ID`).
