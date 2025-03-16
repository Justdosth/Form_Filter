document.addEventListener("DOMContentLoaded", function () {
    // You can now use these lists in JavaScript, for example:
    // console.log("Column Names:", columnNames);
    // console.log(typeof  jsonFieldsMapping);

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

    // Attach event listeners for delete buttons
    document.querySelectorAll(".custom-delete-button").forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.getAttribute("data-user-id"); 
            deleteUser(userId);
        });
    });

    const columnFilter = document.getElementById("columnFilter");

    // Enable multi-select behavior
    columnFilter.addEventListener("mousedown", function (e) {
        e.preventDefault();
        let option = e.target;
        if (option.tagName === "OPTION") {
            option.selected = !option.selected;
            showDynamicFilterOptions();  // Call function after selecting
        }
    });

    columnFilter.addEventListener("change", showDynamicFilterOptions); // Ensure it triggers on selection change
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

function normalizeText(text) {
    if (!text) return "";

    let persianToEnglishNumbers = {
        "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
        "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"
    };
    text = text.replace(/[۰-۹]/g, d => persianToEnglishNumbers[d]);

    let persianToEnglishMap = {
        "ي": "ی", "ك": "ک", "ة": "ه"
    };
    text = text.replace(/[يكة]/g, c => persianToEnglishMap[c]);

    return text.trim().toLowerCase();
}



function showDynamicFilterOptions() {
    const columnFilter = document.getElementById("columnFilter");
    const dynamicFilterContainer = document.getElementById("dynamicFilterContainer");
    const dynamicFilter = document.getElementById("dynamicFilter");
    // Get selected column names based on the text inside selected <option> tags
    const selectedColumnNames = Array.from(document.getElementById("columnFilter").selectedOptions).map(option => option.textContent.trim());  // Get the text of the selected options

    // Clear previous filter options
    dynamicFilter.innerHTML = '';

    let hasDynamicFilter = false;

    // Loop through selected column names and check if they exist in jsonFieldsMapping
    selectedColumnNames.forEach(columnName => {
        // console.log(jsonFieldsMapping[columnName]);
        if (jsonFieldsMapping[columnName]) {
            
            hasDynamicFilter = true;  // ✅ At least one dynamic filter should be shown
            jsonFieldsMapping[columnName].forEach(option => {
                const opt = document.createElement('option');
                opt.value = option;
                opt.textContent = option;
                dynamicFilter.appendChild(opt);
            });
        }
    });

    // Show or hide the dynamic filter container based on available options
    dynamicFilterContainer.style.display = hasDynamicFilter ? 'block' : 'none';
}

function filterTable(clearFilters = false) {
    // If clearing filters, reset table and return
    if (clearFilters) {
        window.location.href = "/view-data";  // Redirect to view-data when clearing filters
        return;
    }

    // let raw_query = document.getElementById("tableFilter").value.trim();
    // let query = encodeURIComponent(raw_query);

    let query = document.getElementById("tableFilter").value.trim();

    let selectedColumns = Array.from(document.getElementById("columnFilter").selectedOptions).map(option => option.value);
    let minValue = document.getElementById("minValue").value;
    let maxValue = document.getElementById("maxValue").value;
    let dynamicFilter = document.getElementById("dynamicFilter").value;

    // Construct query parameters
    let params = new URLSearchParams();
    if (query) params.append("query", query);
    if (selectedColumns.length > 0) params.append("columns", JSON.stringify(selectedColumns));
    if (minValue) params.append("min", minValue);
    if (maxValue) params.append("max", maxValue);
    if (dynamicFilter) params.append("dynamicFilter", dynamicFilter);

    // Fetch filtered data
    fetch(`/search?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            displayTableData(data);
        })
        .catch(error => {
            console.error("Error fetching filtered data:", error);
        });
}

// Attach event listeners
document.getElementById("searchButton").addEventListener("click", () => filterTable(false));
document.getElementById("clearFiltersButton").addEventListener("click", () => filterTable(true));


function displayTableData(data) {
    const tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = ""; // Clear existing table data

    if (!data || data.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='100%'>No data found.</td></tr>";
        return;
    }

    // Generate table rows dynamically
    data.forEach(row => {
        let rowHtml = `<tr>`;
        row.forEach(cell => {
            rowHtml += `<td>${cell}</td>`;
        });

        // Get user_id (assuming it's the first column, adjust if needed)
        let userId = row[0];

        // Add Action buttons (View + Delete)
        rowHtml += `
            <td>
                <button class="custom-swal-button view-acquaintances" data-user-id="${userId}">Acquaintances</button>
                <button class="custom-swal-button view-certificates" data-user-id="${userId}">Certificates</button>
                <button class="custom-swal-button view-work-experience" data-user-id="${userId}">Experience</button>
                <button class="custom-delete-button" data-user-id="${userId}">Delete</button>
            </td>
        `;

        rowHtml += `</tr>`;
        tableBody.innerHTML += rowHtml;
    });
    
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
    // Attach event listeners for delete buttons
    document.querySelectorAll(".custom-delete-button").forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.getAttribute("data-user-id"); 
            deleteUser(userId);
        });
    });
}

/**
 * Sends a delete request to the backend to remove a user and their related data.
 * @param {string} userId - The ID of the user to delete.
 */
function deleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user and all related data?")) return;

    fetch(`/delete_user?user_id=${userId}`, { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("User deleted successfully.");
                filterTable(false); // Refresh the table
            } else {
                alert("Error deleting user: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
}
