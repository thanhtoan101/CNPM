const jwt = require("jsonwebtoken");

function getJwtSecret() {
  const secret = process.env.JWT_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error("JWT_SECRET must contain at least 32 characters. See backend/.env.example.");
  }
  return secret;
}

function signAccessToken(user) {
  return jwt.sign({ id: user.id, email: user.email, role: user.role }, getJwtSecret(), {
    algorithm: "HS256", expiresIn: "1h",
  });
}

module.exports = { getJwtSecret, signAccessToken };
