document.addEventListener("DOMContentLoaded", function () {
    // Selecting all buttons dynamically
    document.querySelectorAll(".view-acquaintances, .view-certificates, .view-work-experience").forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.getAttribute("data-user-id"); // Get user ID
            const tableName = this.classList.contains("view-acquaintances") ? "Acquaintance" :
                              this.classList.contains("view-certificates") ? "Certificate" :
                              "Work_Experience"; // Choose table based on button clicked
            
            fetchRelatedData(userId, tableName); // Call function to fetch data
        });
    });
});


/**
 * Fetch related data from the backend and display it on the page.
 * @param {string} userId - The ID of the user.
 * @param {string} tableName - The table name to fetch data from.
 */
function fetchRelatedData(userId, tableName) {
    fetch(`/get_related_data?user_id=${userId}&table_name=${tableName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Server response was not OK");
            }
            return response.json();
        })
        .then(data => {
            displayRelatedData(data, tableName); // Display the fetched data
        })
        .catch(error => {
            console.error("Error fetching related data:", error);
            document.getElementById("relatedDataContainer").innerHTML = `<p class="error-message">⚠️ Could not load data.</p>`;
        });
}



// Function to show a message
function displayMessage(msg) {
    const messageContainer = document.getElementById("relatedDataContainer");
    messageContainer.innerHTML = `<p class="no-data-message">${msg}</p>`;
}


/**
 * Displays related data in a table format inside the #relatedDataContainer.
 * @param {Array} data - The fetched data from the backend.
 * @param {string} tableName - The table name (used for headings).
 */
function displayRelatedData(data, tableName) {
    const container = document.getElementById("relatedDataContainer");

    // If no data found, show message
    if (!data || data.length === 0) {
        container.innerHTML = `<p class="no-data-message">⚠️ No related data found for ${tableName}.</p>`;
        return;
    }

    // Create table dynamically
    let tableHtml = `<h2>${tableName} Details</h2>`;
    tableHtml += `<table class="related-data-table"><thead><tr>`;

    // Get column names from the first object
    Object.keys(data[0]).forEach(col => {
        tableHtml += `<th>${col}</th>`;
    });
    tableHtml += `</tr></thead><tbody>`;

    // Fill rows with data
    data.forEach(row => {
        tableHtml += `<tr>`;
        Object.values(row).forEach(value => {
            tableHtml += `<td>${value}</td>`;
        });
        tableHtml += `</tr>`;
    });

    tableHtml += `</tbody></table>`;

    // Update the container with the new table
    container.innerHTML = tableHtml;
}