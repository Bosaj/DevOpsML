/**
 * Health check controller for DevOpsML
 */
function getHealthStatus() {
  return {
    service: 'DevOpsML',
    status: 'UP',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  };
}

module.exports = { getHealthStatus };
