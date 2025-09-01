
-- services/api-gateway/plugins/payment-gate.lua
-- Custom APISIX plugin to gate PDF downloads based on payment status in PostgreSQL.

local core = require("apisix.core")
local plugin = require("apisix.plugin")
local http = require("apisix.core.http")
local ngx_re = require("ngx.re")
local cjson = require("cjson")

-- PostgreSQL connection details (should be externalized in production)
-- For demonstration, using direct connection. In production, consider connection pooling.
local PG_HOST = os.getenv("PG_HOST") or "db"
local PG_PORT = os.getenv("PG_PORT") or "5432"
local PG_USER = os.getenv("PG_USER") or "user"
local PG_PASSWORD = os.getenv("PG_PASSWORD") or "password"
local PG_DBNAME = os.getenv("PG_DBNAME") or "solcalc"

local _M = {
    version = 1.0,
    priority = 1000, -- High priority to gate before other plugins
    name = "payment-gate",
    schema = {
        type = "object",
        properties = {
            database_url = {
                type = "string",
                description = "PostgreSQL connection string (e.g., postgresql://user:password@host:port/dbname)"
            }
        }
    }
}

function _M.check_schema(conf)
    return true, nil
end

function _M.new()
    return {
        -- This plugin does not need to store any state per request
    }
end

function _M.access(conf, ctx)
    local uri = ngx.var.uri
    local project_id

    -- Extract project_id from URI (e.g., /api/download/1234-...)
    local m, err = ngx_re.match(uri, "/api/download/([0-9a-fA-F%-]+)", "jo")
    if m then
        project_id = m[1]
    else
        core.log.warn("payment-gate: could not extract project_id from URI: ", uri)
        return http.exit(400, cjson.encode({error = "Invalid project ID format in URI"}))
    end

    if not project_id then
        core.log.warn("payment-gate: project_id is nil for URI: ", uri)
        return http.exit(400, cjson.encode({error = "Project ID is missing"}))
    end

    -- Use the database_url from plugin config if provided, otherwise use env vars
    local db_url = conf.database_url or string.format("postgresql://%s:%s@%s:%s/%s",
                                                      PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DBNAME)

    local pg = require("resty.postgres").new()
    local ok, err = pg:connect(db_url)

    if not ok then
        core.log.error("payment-gate: failed to connect to PostgreSQL: ", err)
        return http.exit(500, cjson.encode({error = "Database connection error"}))
    end

    local res, err = pg:query("SELECT status FROM projects WHERE id = $1", project_id)
    if not res then
        core.log.error("payment-gate: failed to query project status: ", err)
        pg:close()
        return http.exit(500, cjson.encode({error = "Database query error"}))
    end

    local project_status = nil
    if #res > 0 and res[1] and res[1].status then
        project_status = res[1].status
    end

    pg:close()

    if project_status == "paid" then
        core.log.info("payment-gate: project ", project_id, " is paid. Allowing access.")
        return -- Allow request to proceed
    else
        core.log.warn("payment-gate: project ", project_id, " status is '", project_status or "nil", "'. Denying access.")
        return http.exit(402, cjson.encode({error = "Payment Required: Project not paid"}))
    end
end

return _M
