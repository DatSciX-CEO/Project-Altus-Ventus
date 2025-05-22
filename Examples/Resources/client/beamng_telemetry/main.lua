
-- main.lua
local socket = require("socket")
local udp = socket.udp()
udp:settimeout(0)
udp:setpeername("YOUR_PI_IP_HERE", 4444)  -- Replace with Raspberry Pi IP

local function sendTelemetry()
    local vel = obj:getVelocity()
    local data = string.format("{\"vel\":[%.2f, %.2f, %.2f]}", vel.x, vel.y, vel.z)
    udp:send(data)
end

M = {}

function M.updateGFX(dt)
    sendTelemetry()
end

return M
