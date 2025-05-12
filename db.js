const sql = require('mssql');

const config = {
  server: 'localhost', // or your SQL Server name
  database: 'AVIS_MAIN1', // <-- change this
  options: {
    trustedConnection: true,
    trustServerCertificate: true
  },
  authentication: {
    type: 'ntlm',
    options: {
      domain: 'WORKGROUP', // or your actual domain name
      userName: '', // blank = use Windows authentication
      password: ''
    }
  }
};

async function connectToDb() {
  try {
    const pool = await sql.connect(config);
    console.log('✅ Connected to SQL Server');
    return pool;
  } catch (err) {
    console.error('❌ DB Connection Error:', err);
    throw err;
  }
}

module.exports = { connectToDb, sql };
