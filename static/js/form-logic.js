function toggleCountryField(selectElement) {
    const textField = document.getElementById('country-details'); // Target the correct div
    if (selectElement.value === 'ساکن شهرستان') {
        textField.style.display = 'block'; // Show the field
        const inputField = textField.querySelector('input');
        inputField.required = true; // Make the input field required
    } else {
        textField.style.display = 'none'; // Hide the field
        const inputField = textField.querySelector('input');
        inputField.required = false; // Remove required
        inputField.value = ''; // Clear the value
    }
}

function validateForm(event) {
    let isValid = true;
    let firstInvalidElement = null;

    // List of required fields (adjust based on backend logic)
    const requiredFields = ["نام", "نام خانوادگی", "جنس", "وضعیت تاهل", "اطلاعات آدرس"];
    
    requiredFields.forEach((field) => {
        const inputElement = document.getElementById(field);
        const errorElement = document.getElementById(`${field}-error`);

        // Clear previous error messages
        errorElement.textContent = "";
        inputElement.classList.remove("error");

        // Validate field
        if (!inputElement.value.trim() || (inputElement.tagName === "SELECT" && !inputElement.value)) {
            errorElement.textContent = `لطفاً ${field} را وارد کنید.`;
            errorElement.style.display = "block"; // Show error message
            inputElement.classList.add("error"); // Highlight field
            isValid = false; // Mark form as invalid
            
            // Store the first invalid element
            if (!firstInvalidElement) {
                firstInvalidElement = inputElement;
            }
        } else {
            errorElement.style.display = "none"; // Hide error message
        }
    });

    // Scroll to the first invalid element
    if (!isValid && firstInvalidElement) {
        firstInvalidElement.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // Prevent form submission if invalid
    if (!isValid) {
        event.preventDefault();
    }
}
