const express = require('express');
const { connectToDb, sql } = require('./db');
const app = express();

app.use(express.json());

app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const pool = await connectToDb();
    const result = await pool
      .request()
      .input('username', sql.VarChar, username)
      .query('SELECT * FROM users WHERE username = @username');

    const user = result.recordset[0];

    if (!user) {
      return res.status(401).send('User not found');
    }

    if (user.password === password) {
      res.send('✅ Login successful');
    } else {
      res.status(401).send('❌ Invalid password');
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('❌ Server error');
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
