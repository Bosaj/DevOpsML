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

function checkLiveness() {
  return true;
}

function checkReadiness() {
  return true;
}

module.exports = {
  getHealthStatus,
  checkLiveness,
  checkReadiness
};
