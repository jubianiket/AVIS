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
          table.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
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
      <label>Name:</label><input type="text" name="name" required><br>
      <label>Part Number:</label><input type="text" name="partNumber" required><br>
      <button type="submit">Add Entry</button>`;
  } else if (tab === 'consumers') {
    form.innerHTML = `
      <label>Consumer Name:</label><input type="text" name="name" required><br>
	  <label>Consumer Address:</label><input type="text" name="Address" required><br>
	  <label>Consumer GST NO:</label><input type="text" name="GST NO" required><br>
	  <label>Consumer STATE CODE:</label><input type="text" name="STATE CODE" required><br>
      <label>Consumer Contact:</label><input type="text" name="contactno" required>
	  <label>Consumer Email:</label><input type="text" name="Email" required><br>
      <button type="submit">Add Entry</button>`;
  } else if (tab === 'suppliers') {
    form.innerHTML = `
      <label>Supplier Name:</label><input type="text" name="name" required><br>
      <label>Address:</label><input type="text" name="address" required><br>
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
