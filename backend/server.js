require("dotenv").config();
const verifyToken = require("./authMiddleware");
const express = require("express");
const cors = require("cors");
const pool = require("./db");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcrypt");

const app = express();

app.use(cors());
app.use(express.json());

console.log("SERVER VERSION 123");

/*
==================================
LOGIN API
==================================
*/
app.post("/auth/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        message: "Email and password are required",
      });
    }

    const result = await pool.query(
      "SELECT * FROM users WHERE email = $1",
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: "User not found",
      });
    }

    const user = result.rows[0];

    const validPassword = await bcrypt.compare(
      password,
      user.password_hash
    );

    if (!validPassword) {
      return res.status(401).json({
        message: "Invalid password",
      });
    }

    const token = jwt.sign(
      {
        id: user.id,
        email: user.email,
        role: user.role,
      },
      process.env.JWT_SECRET || "SECRET_KEY",
      {
        expiresIn: "1h",
      }
    );

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
      error: err.message,
    });
  }
});

/*
==================================
DATABASE TEST
==================================
*/
pool.query("SELECT NOW()")
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
      error: err.message,
    });
  }
});

/*
==================================
LIST TABLES
==================================
*/
app.get("/tables", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: err.message,
    });
  }
});

/*
==================================
TABLE SCHEMA
==================================
*/
app.get("/schema/:table", async (req, res) => {
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
      error: err.message,
    });
  }
});

/*
==================================
LIST USERS
==================================
*/
app.get("/users", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, email, role
      FROM users
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: err.message,
    });
  }
});

/*
==================================
FULL USERS
==================================
*/
app.get("/users/full", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT *
      FROM users
      LIMIT 5
    `);

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({
      error: err.message,
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
      error: err.message
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
      error: err.message
    });

  }

});
app.get("/orders", verifyToken, async (req, res) => {

  try {

    const result = await pool.query(
      "SELECT * FROM orders"
    );

    res.json(result.rows);

  } catch (err) {

    res.status(500).json({
      error: err.message
    });

  }

});
/*
==================================
API tạo lap course order
==================================
*/
app.post("/labs", verifyToken, async (req, res) => {
  try {

    const { name, address, description, rating } = req.body;

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
        rating
      ]
    );

    res.json(result.rows[0]);

  } catch (err) {

    res.status(500).json({
      error: err.message
    });

  }
});
app.post("/courses", verifyToken, async (req, res) => {

  const {
    course_name,
    description,
    status,
    start_date,
    end_date
  } = req.body;

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
app.post("/orders", verifyToken, async (req, res) => {

  const {
    lab_id,
    service_id,
    total_price
  } = req.body;

  const result = await pool.query(
    `
    INSERT INTO orders
    (
      user_id,
      lab_id,
      service_id,
      status,
      total_price
    )
    VALUES ($1,$2,$3,$4,$5)
    RETURNING *
    `,
    [
      req.user.id,
      lab_id,
      service_id,
      "pending",
      total_price
    ]
  );

  res.json(result.rows[0]);

});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});