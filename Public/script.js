function showTabContent(tab) {
  fetch(`/tab/${tab}`)
    .then(res => res.text())
    .then(html => {
      document.getElementById('tab-content').innerHTML = html;
    });
}

function searchData(tab) {
  const query = document.getElementById('search-box').value;
  if (query) {
    fetch(`/search/${tab}?query=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        const div = document.getElementById('search-results');
        div.innerHTML = '';
        if (data.length) {
          const table = document.createElement('table');
          const headers = Object.keys(data[0]);

          // Mapping SQL column names to display names
          const columnDisplayNames = {
            inventory: {
              INVN_ID: "ID",
              INVN_NAME: "Item Name",
              INVN_RATE: "Rate",
              INVN_CODE: "Item Code",
              INVN_RATE_CURRENCY: "Currency"
            },
            customers: {
              CUST_ID: "ID",
              CUST_NAME: "Customer Name",
              CUST_BILL_ADD: "Billing Address",
              CUST_SHIP_ADD: "Shipping Address",
              CUST_CONTACT: "Contact Number",
              CUST_EMAIL_ID: "Email",
              CUST_GST_NO: "GST Number",
              CUST_STATE_CODE_NO: "State Code"
            },
            suppliers: {
              SUP_ID: "ID",
              SUP_NAME: "Supplier Name",
              SUP_BILL_ADD: "Billing Address",
              SUP_SHIP_ADD: "Shipping Address",
              SUP_CONTACT: "Contact Number",
              SUP_EMAIL_ID: "Email",
              SUP_GST_NO: "GST Number",
              SUP_STATE_CODE_NO: "State Code"
            }
          };

          const displayMap = columnDisplayNames[tab] || {};

          table.innerHTML = `<tr>${headers.map(h => `<th>${displayMap[h] || h}</th>`).join('')}</tr>`;
          data.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(h => {
              const td = document.createElement('td');
              td.textContent = row[h];
              tr.appendChild(td);
            });
            table.appendChild(tr);
          });
          div.appendChild(table);
        } else {
          div.innerHTML = "<p>No results found</p>";
        }
      });
  }
}

function showForm(tab) {
  const formContainer = document.getElementById('form-container');
  formContainer.innerHTML = '';
  const form = document.createElement('form');

  if (tab === 'inventory') {
    form.innerHTML = `
      <label>Item Name:</label><input type="text" name="name" required><br>
      <label>Item Code:</label><input type="text" name="partNumber" required><br>
      <button type="submit">Add Entry</button>`;
  } else if (tab === 'customers') {
    form.innerHTML = `
      <label>Customer Name:</label><input type="text" name="name" required><br>
      <label>Billing Address:</label><input type="text" name="Address" required><br>
      <label>GST Number:</label><input type="text" name="GST NO" required><br>
      <label>State Code:</label><input type="text" name="STATE CODE" required><br>
      <label>Contact Number:</label><input type="text" name="contactno" required><br>
      <label>Email:</label><input type="text" name="Email" required><br>
      <button type="submit">Add Entry</button>`;
  } else if (tab === 'suppliers') {
    form.innerHTML = `
      <label>Supplier Name:</label><input type="text" name="name" required><br>
      <label>Billing Address:</label><input type="text" name="address" required><br>
      <label>Shipping Address:</label><input type="text" name="shipping" required><br>
      <label>Contact Number:</label><input type="text" name="contact" required><br>
      <label>Email:</label><input type="text" name="email" required><br>
      <label>GST Number:</label><input type="text" name="gst" required><br>
      <label>State Code:</label><input type="text" name="statecode" required><br>
      <button type="submit">Add Entry</button>`;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    const formData = new FormData(form);
    console.log(Object.fromEntries(formData.entries()));
    alert("Entry added successfully! (Feature under construction)");
    form.reset();
  });

  formContainer.appendChild(form);
}
