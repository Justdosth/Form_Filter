document.addEventListener("DOMContentLoaded", function () {
    // Select all buttons that fetch related data
    document.querySelectorAll(".view-acquaintances, .view-certificates, .view-work-experience")
        .forEach(button => {
            button.addEventListener("click", function () {
                let userId = this.getAttribute("data-user-id"); // Get the User ID
                let actionType = this.classList.contains("view-acquaintances") ? "acquaintances" :
                                 this.classList.contains("view-certificates") ? "certificates" :
                                 "work_experience"; // Determine which data to fetch

                fetchRelatedData(userId, actionType); // Call function to fetch data
            });
        });
});

/**
 * Fetches related data from the server via AJAX.
 * @param {string} userId - The ID of the selected user.
 * @param {string} actionType - The type of data to fetch (acquaintances, certificates, work_experience).
 */
function fetchRelatedData(userId, dataType) {
    fetch(`/fetch_related_data/${dataType}/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.data.length === 0) {
                    displayMessage(`No ${dataType} data found for this user.`);
                } else {
                    displayRelatedData(data.data, dataType);
                }
            } else {
                displayMessage("Error fetching data. Please try again.");
            }
        })
        .catch(() => displayMessage("Error connecting to the server."));
}

// Function to show a message
function displayMessage(msg) {
    const messageContainer = document.getElementById("relatedDataContainer");
    messageContainer.innerHTML = `<p class="no-data-message">${msg}</p>`;
}


/**
 * Displays the fetched related data inside the container.
 * @param {Object} data - The JSON data received from the server.
 * @param {string} actionType - The type of data being displayed.
 */
function displayRelatedData(data, actionType) {
    let container = document.getElementById("relatedDataContainer");
    container.innerHTML = ""; // Clear previous content

    if (data.length === 0) {
        container.innerHTML = `<p>No ${actionType.replace("_", " ")} found for this user.</p>`;
        return;
    }

    // Create table structure dynamically
    let table = document.createElement("table");
    table.classList.add("styled-table");

    // Create table header
    let thead = document.createElement("thead");
    let headerRow = document.createElement("tr");
    
    // Extract keys from the first object as column headers
    Object.keys(data[0]).forEach(colName => {
        let th = document.createElement("th");
        th.textContent = colName;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    let tbody = document.createElement("tbody");
    data.forEach(row => {
        let tr = document.createElement("tr");
        Object.values(row).forEach(cellValue => {
            let td = document.createElement("td");
            td.textContent = cellValue;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table); // Append table to container
}
