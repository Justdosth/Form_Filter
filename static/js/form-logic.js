function toggleCountryField(selectElement) {
    const countryDetails = document.getElementById('country-details');
    const countryInput = document.getElementById('country-name');

    if (selectElement.value === 'ساکن شهرستان') {
        countryDetails.style.display = 'block';
        countryInput.required = true; // Make it required when visible
    } else {
        countryDetails.style.display = 'none';
        countryInput.required = false; // Remove required if hidden
        countryInput.value = ''; // Clear the value when hidden
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

document.addEventListener("DOMContentLoaded", function () {
    const datePicker = document.getElementById('تاریخ تولد');
    console.log(datePicker)
    $(datePicker).persianDatepicker({
        format: 'YYYY/MM/DD',
        observer: true,
        initialValueType: 'persian',
    });
});