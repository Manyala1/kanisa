// main.js

// Example: Showing an alert when a new member is added
document.addEventListener('DOMContentLoaded', function() {
    const memberForm = document.querySelector('form[action="/add_member"]');
    if (memberForm) {
        memberForm.addEventListener('submit', function(event) {
            alert('Member added successfully!');
        });
    }
});
