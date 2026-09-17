const jwt = require("jsonwebtoken");
const { getJwtSecret } = require("./authConfig");

function verifyToken(req, res, next) {

  const authHeader = req.headers.authorization;

  if (typeof authHeader !== "string" || !/^Bearer \S+$/i.test(authHeader)) {
    return res.status(401).json({
      message: "A Bearer access token is required"
    });
  }

  const token = authHeader.split(" ")[1];

  try {

    const decoded = jwt.verify(
      token,
      getJwtSecret(),
      { algorithms: ["HS256"] }
    );

    if (!decoded || typeof decoded !== "object" || !decoded.id || !decoded.role) {
      return res.status(401).json({ message: "Invalid token" });
    }
    req.user = decoded;

    next();

  } catch (err) {

    return res.status(401).json({
      message: "Invalid token"
    });

  }
}

module.exports = verifyToken;
module.exports.requireRoles = (...roles) => (req, res, next) => {
  if (!roles.includes(req.user?.role)) return res.status(403).json({ message: "This role cannot perform the action" });
  next();
};
module.exports.requireAdmin = (req, res, next) => {
  if (req.user?.role !== "admin") return res.status(403).json({ message: "Administrator access required" });
  next();
};
