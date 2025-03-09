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

// function filterTable() {
//     let input = normalizeText(document.getElementById("tableFilter").value);
//     let minValue = document.getElementById("minValue").value;
//     let maxValue = document.getElementById("maxValue").value;
//     let table = document.getElementById("dataTable");
//     let rows = table.getElementsByTagName("tr");
//     let selectedColumns = Array.from(document.getElementById("columnFilter").selectedOptions).map(opt => parseInt(opt.value));

//     for (let i = 1; i < rows.length; i++) { // Start from 1 to skip the header
//         let cells = rows[i].getElementsByTagName("td");
//         let rowContainsFilter = false;

//         for (let colIndex of selectedColumns) {
//             let cellText = normalizeText(cells[colIndex]?.textContent);

//             // If a range is applied
//             if (minValue || maxValue) {
//                 let cellValue = parseFloat(cellText);
//                 let minCheck = minValue === "" || (cellValue && cellValue >= parseFloat(minValue));
//                 let maxCheck = maxValue === "" || (cellValue && cellValue <= parseFloat(maxValue));

//                 if (minCheck && maxCheck) {
//                     rowContainsFilter = true;
//                     break;
//                 }
//             }
//             // Normal text search
//             else if (cellText.includes(input)) {
//                 rowContainsFilter = true;
//                 break;
//             }
//         }

//         rows[i].style.display = rowContainsFilter ? "" : "none";
//     }
// }

function filterTable() {
    const searchTerm = normalizeText(document.getElementById('tableFilter').value);
    const minValue = document.getElementById('minValue').value;
    const maxValue = document.getElementById('maxValue').value;
    const selectedColumns = Array.from(document.getElementById("columnFilter").selectedOptions).map(option => option.textContent.trim());
    const dynamicFilterValue = document.getElementById('dynamicFilter') ? normalizeText(document.getElementById('dynamicFilter').value) : '';
    // Filter rows based on search term, selected columns, range, and dynamic filter
    const rows = document.querySelectorAll('#dataTable tbody tr');
    
    rows.forEach(row => {
        let rowText = Array.from(row.cells).map(cell => normalizeText(cell.textContent.toLowerCase()));
        let isMatch = true;
        // 1. Check for text search in selected columns
        if (selectedColumns.length > 0 & searchTerm) {
            console.log(searchTerm);
            isMatch = selectedColumns.some(colIndex => rowText[colIndex].includes(searchTerm));
        }

        // 2. Apply range filter if any
        if (minValue || maxValue) {
            const numericDataCells = Array.from(row.cells).filter(cell => !isNaN(parseFloat(cell.textContent)));
            if (numericDataCells.length) {
                const cellValue = parseFloat(numericDataCells[0].textContent);
                if ((minValue && cellValue < minValue) || (maxValue && cellValue > maxValue)) {
                    isMatch = false;
                }
            }
        }

        // 3. Dynamic filter check
        if (dynamicFilterValue) {
            const dynamicColumnIndex = columnNames.indexOf(selectedColumns[0]); // Get correct column index
            
            if (dynamicColumnIndex !== -1) {  // ✅ Ensure the index is valid
                const dynamicColumnValue = row.cells[dynamicColumnIndex]?.textContent?.trim() || ''; // ✅ Handle undefined cases safely
                
                if (!normalizeText(dynamicColumnValue).includes(dynamicFilterValue.toLowerCase())) {
                    isMatch = false;
                }
            }
        }


        // Show or hide the row based on match
        row.style.display = isMatch ? '' : 'none';
    });
}

