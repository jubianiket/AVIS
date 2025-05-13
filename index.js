// index.js
const express = require('express');
const sql = require('mssql/msnodesqlv8');
const bodyParser = require('body-parser');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const config = {
  connectionString: 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Trusted_Connection=Yes;Database=AVIS_MAIN;',
  driver: 'msnodesqlv8'
};

app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <link rel="stylesheet" href="/styles.css">
        <script src="/script.js" defer></script>
      </head>
      <body>
        <h2>Welcome to AVIS PVT LTD</h2>
        <form action="/login" method="post">
          <label><input type="checkbox" checked disabled> Login using Windows Authentication</label><br><br>
          <button type="submit">Login as Admin</button>
        </form>
      </body>
    </html>
  `);
});

app.post('/login', async (req, res) => {
  try {
    await sql.connect(config);
    res.send(`
      <html>
        <head>
          <link rel="stylesheet" href="/styles.css">
          <script src="/script.js" defer></script>
        </head>
        <body>
          <div class="sidebar">
            <ul>
              <li><a href="#" onclick="showTabContent('dashboard')">Dashboard</a></li>
              <li><a href="#" onclick="showTabContent('inventory')">Inventory</a></li>
              <li><a href="#" onclick="showTabContent('invoice')">Invoice</a></li>
              <li><a href="#" onclick="showTabContent('payments')">Payments</a></li>
              <li><a href="#" onclick="showTabContent('history')">History</a></li>
              <li><a href="#" onclick="showTabContent('customers')">Customers</a></li>
              <li><a href="#" onclick="showTabContent('suppliers')">Suppliers</a></li>
              <li><a href="#" onclick="showTabContent('help')">Help</a></li>
            </ul>
          </div>
          <div id="tab-content"></div>
        </body>
      </html>
    `);
  } catch (err) {
    res.status(500).send('Login failed: ' + err.message);
  }
});

app.get('/tab/:tab', (req, res) => {
  const tab = req.params.tab;
  const capitalized = tab.charAt(0).toUpperCase() + tab.slice(1);
  res.send(`
    <h2>${capitalized} Section</h2>
    <select id="search-filter">
      <option value="name">Search by Name</option>
    </select>
    <input type="text" id="search-box" placeholder="Enter search term..." />
    <button onclick="searchData('${tab}')">Search</button>
    <div id="search-results"></div>
    <button onclick="showForm('${tab}')">Add New</button>
    <div id="form-container"></div>
  `);
});

app.get('/search/:tab', async (req, res) => {
  const tab = req.params.tab;
  const query = req.query.query;

  try {
    await sql.connect(config);
    let queryStr = '';

    if (tab === 'inventory') {
      queryStr = `SELECT * FROM [AVIS_MAIN].[dbo].[inventory_details] WHERE INVN_NAME LIKE @query`;
    } else if (tab === 'customers') {
      queryStr = `SELECT * FROM [AVIS_MAIN].[dbo].[cust_details] WHERE CUST_NAME LIKE @query`;
    } else if (tab === 'suppliers') {
      queryStr = `SELECT * FROM [AVIS_MAIN].[dbo].[sup_details] WHERE SUP_NAME LIKE @query`;
    }

    const request = new sql.Request();
    request.input('query', sql.NVarChar, `%${query}%`);
    const result = await request.query(queryStr);

    res.json(result.recordset);
  } catch (err) {
    console.error('Database query error:', err);
    res.status(500).json({ error: 'Database query failed', message: err.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});