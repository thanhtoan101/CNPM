require("dotenv").config();
const verifyToken = require("./authMiddleware");
const { requireAdmin, requireRoles } = require("./authMiddleware");
const { getJwtSecret, signAccessToken } = require("./authConfig");
const express = require("express");
const cors = require("cors");
const pool = require("./db");
const bcrypt = require("bcrypt");

const app = express();

app.use(cors());
app.use(express.json());


/*
==================================
LOGIN API
==================================
*/
app.post("/auth/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (typeof email !== "string" || typeof password !== "string" || !email.trim() || !password) {
      return res.status(400).json({
        message: "Email and password are required",
      });
    }

    const result = await pool.query(
      "SELECT * FROM users WHERE email = $1",
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({
        message: "Invalid email or password",
      });
    }

    const user = result.rows[0];

    const validPassword = await bcrypt.compare(
      password,
      user.password_hash
    );

    if (!validPassword) {
      return res.status(401).json({
        message: "Invalid email or password",
      });
    }

    const token = signAccessToken(user);

    return res.status(200).json({
      message: "Login successful",
      token,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
      },
    });

  } catch (err) {
    console.error("LOGIN ERROR:", err);

    return res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
DATABASE TEST
==================================
*/
if (require.main === module) pool.query("SELECT NOW()")
  .then(() => console.log("DATABASE CONNECTED"))
  .catch(err => console.log("DB ERROR:", err.message));

/*
==================================
ROOT
==================================
*/
app.get("/", async (req, res) => {
  try {
    const result = await pool.query("SELECT NOW()");
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
LIST TABLES
==================================
*/
app.get("/tables", verifyToken, requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
TABLE SCHEMA
==================================
*/
app.get("/schema/:table", verifyToken, requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(
      `
      SELECT
        column_name,
        data_type
      FROM information_schema.columns
      WHERE table_name = $1
      `,
      [req.params.table]
    );

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
LIST USERS
==================================
*/
app.get("/users", verifyToken, requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, email, role
      FROM users
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
FULL USERS
==================================
*/
app.get("/users/full", verifyToken, requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, email, role
      FROM users
      LIMIT 5
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: "The request could not be completed",
    });
  }
});

/*
==================================
START SERVER
==================================
*/
const PORT = process.env.PORT || 3000;
app.get("/labs", verifyToken, async (req, res) => {

  try {

    const result = await pool.query(
      "SELECT * FROM labs"
    );

    res.json(result.rows);

  } catch (err) {

    res.status(500).json({
      error: "The request could not be completed"
    });

  }

});
app.get("/courses", verifyToken, async (req, res) => {

  try {

    const result = await pool.query(
      "SELECT * FROM courses"
    );

    res.json(result.rows);

  } catch (err) {

    res.status(500).json({
      error: "The request could not be completed"
    });

  }

});
app.get("/orders", verifyToken, async (req, res) => {

  try {

    const result = await pool.query(
      req.user.role === "admin" ? "SELECT * FROM orders" : "SELECT * FROM orders WHERE user_id = $1",
      req.user.role === "admin" ? [] : [req.user.id]
    );

    res.json(result.rows);

  } catch (err) {

    res.status(500).json({
      error: "The request could not be completed"
    });

  }

});
/*
==================================
API tạo lap course order
==================================
*/
app.post("/labs", verifyToken, requireRoles("admin", "lab_owner"), async (req, res) => {
  try {

    const { name, address, description = "" } = req.body;
    if (typeof name !== "string" || !name.trim() || name.length > 200 || typeof address !== "string" || !address.trim() || address.length > 500 || typeof description !== "string" || description.length > 5000) {
      return res.status(400).json({ message: "Valid lab name, address and description are required" });
    }

    const result = await pool.query(
      `
      INSERT INTO labs
      (owner_id, name, address, description, rating)
      VALUES ($1,$2,$3,$4,$5)
      RETURNING *
      `,
      [
        req.user.id,
        name,
        address,
        description,
        0
      ]
    );

    res.json(result.rows[0]);

  } catch (err) {

    res.status(500).json({
      error: "The request could not be completed"
    });

  }
});
app.post("/courses", verifyToken, requireRoles("admin", "expert"), async (req, res) => {

  const {
    course_name,
    description,
    status,
    start_date,
    end_date
  } = req.body;

  if (typeof course_name !== "string" || !course_name.trim() || course_name.length > 200 || typeof description !== "string" || description.length > 5000 || !["draft", "published", "cancelled"].includes(status) || !Number.isFinite(Date.parse(start_date)) || !Number.isFinite(Date.parse(end_date)) || Date.parse(end_date) < Date.parse(start_date)) {
    return res.status(400).json({ message: "Valid course details, status and date range are required" });
  }

  const result = await pool.query(
    `
    INSERT INTO courses
    (
      course_name,
      description,
      status,
      start_date,
      end_date
    )
    VALUES ($1,$2,$3,$4,$5)
    RETURNING *
    `,
    [
      course_name,
      description,
      status,
      start_date,
      end_date
    ]
  );

  res.json(result.rows[0]);

});
app.post("/orders", verifyToken, requireRoles("admin", "photographer"), async (req, res) => {

  const {
    lab_id,
    service_id,
    quantity = 1
  } = req.body;

  if (![lab_id, service_id, quantity].every(Number.isSafeInteger) || lab_id < 1 || service_id < 1 || quantity < 1 || quantity > 100) {
    return res.status(400).json({ message: "Valid lab_id, service_id and quantity (1-100) are required" });
  }
  const service = await pool.query("SELECT price FROM services WHERE id = $1 AND lab_id = $2 AND active = TRUE", [service_id, lab_id]);
  if (!service.rows.length) return res.status(400).json({ message: "The selected service is not available at this lab" });
  const total_price = Number(service.rows[0].price) * quantity;

  const result = await pool.query(
    `
    INSERT INTO orders
    (
      user_id,
      lab_id,
      service_id,
      status,
      total_price,
      quantity
    )
    VALUES ($1,$2,$3,$4,$5,$6)
    RETURNING *
    `,
    [
      req.user.id,
      lab_id,
      service_id,
      "pending",
      total_price,
      quantity
    ]
  );

  res.json(result.rows[0]);

});

app.use((error, req, res, next) => {
  if (error.type === "entity.parse.failed") return res.status(400).json({ message: "Invalid JSON body" });
  console.error("REQUEST ERROR:", error.message);
  res.status(500).json({ message: "The request could not be completed" });
});

if (require.main === module) {
  getJwtSecret();
  app.listen(PORT, "127.0.0.1", () => {
    console.log(`Server running on http://127.0.0.1:${PORT}`);
  });
}
module.exports = app;
