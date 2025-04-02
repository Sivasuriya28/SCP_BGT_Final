/*global fetch*/
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('budget-form');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const category = document.getElementById('category').value.trim();
    const allocated_amount = parseFloat(document.getElementById('allocated_amount').value);

    // Validation
    if (!category || isNaN(allocated_amount) || allocated_amount <= 0) {
      alert("Please provide a valid category and a positive amount.");
      return;
    }

    const payload = {
      category,
      allocated_amount
    };

    fetch('/api/budgets/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()  // ✅ CSRF token added here
      },
      body: JSON.stringify(payload)
    })
    .then(response => {
      if (response.ok) {
        alert('Budget added successfully.');
        window.location.href = '/';
      } else {
        return response.text().then(text => {
          console.error("Server error response:", text);
          alert('Failed to add budget. Check console for details.');
        });
      }
    })
    .catch(error => {
      console.error("Network error:", error);
      alert('Network error: ' + error.message);
    });
  });

  // Helper function to get CSRF token from cookies
  function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
