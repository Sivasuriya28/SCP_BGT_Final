/*global fetch*/
document.addEventListener('DOMContentLoaded', function () {
  // Load Budget Summary
  fetch('/api/summary/')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.getElementById('summary-table-body');

      data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${item.category}</td>
          <td>€${parseFloat(item.allocated_amount).toFixed(2)}</td>
          <td>€${parseFloat(item.spent_amount).toFixed(2)}</td>
          <td>€${parseFloat(item.remaining_amount).toFixed(2)}</td>
          <td class="${item.status === 'Over Budget' ? 'status-over' : 'status-within'}">
            ${item.status}
          </td>
          <td>
            <a href="/budget/edit/${item.id}/" class="btn edit-btn">Edit</a>
            <a href="/budget/delete/${item.id}/" class="btn delete-btn">Delete</a>
          </td>
        `;
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error fetching summary:', error);
    });

  // Load Expense Summary
  fetch('/api/expenses/')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.getElementById('expense-summary-body');

      data.forEach(item => {
        const amount = item.converted_amount ?? item.amount;
        const currency = item.converted_currency ?? item.currency ?? 'EUR';

        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${item.category}</td>
          <td>${item.description || ''}</td>
          <td>
            €${parseFloat(item.converted_amount ?? item.amount).toFixed(2)}
            <br><small>(${item.amount} ${item.currency})</small>
          </td>
          <td>${item.date}</td>
          <td>${item.currency}</td>
          <td>
            <a href="/expense/edit/${item.transaction_id}/" class="btn edit-btn">Edit</a>
            <a href="/expense/delete/${item.transaction_id}/" class="btn delete-btn">Delete</a>
          </td>
        `;
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error fetching expenses:', error);
    });
});
