/*global fetch*/
document.addEventListener("DOMContentLoaded", function () {
  function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  const form = document.getElementById("expense-form");
  const currencyField = document.getElementById("currency");
  const amountField = document.getElementById("amount");
  const convertedDisplay = document.getElementById("converted-result");
  const convertedHiddenField = document.getElementById("converted_amount");

  async function updateConvertedAmount() {
    const amount = parseFloat(amountField.value);
    const currency = currencyField.value;

    if (!amount || isNaN(amount) || currency === "EUR") {
      convertedDisplay.textContent = "";
      convertedHiddenField.value = "";
      return;
    }

    try {
      const response = await fetch("/api/convert/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
          amount,
          from_currency: currency,
          to_currency: "EUR",
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const converted = result.converted_amount;
        convertedDisplay.textContent = `Approx. €${converted.toFixed(2)}`;
        convertedHiddenField.value = converted; // Set hidden value
      } else {
        convertedDisplay.textContent = "Conversion failed.";
        convertedHiddenField.value = "";
      }
    } catch (error) {
      console.error("Conversion error:", error);
      convertedDisplay.textContent = "Error converting currency.";
      convertedHiddenField.value = "";
    }
  }

  currencyField.addEventListener("change", updateConvertedAmount);
  amountField.addEventListener("input", updateConvertedAmount);

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const data = {
      category: document.getElementById("category").value.trim(),
      amount: parseFloat(amountField.value),
      description: document.getElementById("description").value.trim(),
      date: document.getElementById("date").value,
      currency: currencyField.value,
      converted_amount: parseFloat(convertedHiddenField.value) || null,
      converted_currency: "EUR"
    };

    if (!data.category || isNaN(data.amount) || data.amount <= 0 || !data.date || !data.currency) {
      alert("Please fill in all required fields with valid values.");
      return;
    }

    const today = new Date().toISOString().split("T")[0];
    if (data.date > today) {
      alert("Date cannot be in the future.");
      return;
    }

    try {
      const response = await fetch("/api/expenses/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert("Expense added successfully!");
        window.location.href = "/";
      } else {
        const errorData = await response.json();
        console.error("Error:", errorData);
        alert("Error adding expense. Check console for details.");
      }
    } catch (error) {
      console.error("Exception:", error);
      alert("An error occurred while submitting the form.");
    }
  });

  updateConvertedAmount(); // trigger initial conversion
});
