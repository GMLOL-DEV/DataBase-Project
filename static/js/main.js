/* ============================================
   JUDICIAL CASE MANAGEMENT SYSTEM - JAVASCRIPT
   ============================================ */

// Search table functionality
function searchTable(searchInputId, tableId) {
    const input = document.getElementById(searchInputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let found = false;
        const td = tr[i].getElementsByTagName('td');
        
        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        if (found) {
            tr[i].style.display = '';
        } else {
            tr[i].style.display = 'none';
        }
    }
}

// Filter cases by status
function filterCasesByStatus(status) {
    const table = document.getElementById('caseTable');
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        const row = tr[i];
        const rowStatus = row.getAttribute('data-status');
        
        if (status === 'all') {
            row.style.display = '';
        } else {
            if (rowStatus === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    }

    // Update active button
    const buttons = document.querySelectorAll('.filter-buttons .btn');
    buttons.forEach(btn => {
        btn.classList.remove('active-filter');
    });
    event.target.classList.add('active-filter');
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Confirm before deleting
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this?');
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#e74c3c';
        } else {
            field.style.borderColor = '#dfe6e9';
        }
    });

    if (!isValid) {
        alert('Please fill in all required fields.');
    }

    return isValid;
}

// Case search by case ID
function searchCaseByCaseId() {
    const caseId = document.getElementById('caseIdSearch').value;
    
    if (!caseId) {
        alert('Please enter a Case ID');
        return;
    }

    fetch(`/admin/search-case?q=${caseId}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error searching for case');
        });
}

// Search cases by judge ID
function searchCasesByJudgeId() {
    const judgeId = document.getElementById('judgeIdSearch').value;
    
    if (!judgeId) {
        alert('Please enter a Judge ID');
        return;
    }

    fetch(`/judge/search-by-id?judge_id=${judgeId}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error searching for cases');
        });
}

// Display search results
function displaySearchResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    if (!data || data.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
        return;
    }

    let html = '<table class="data-table"><thead><tr>';
    html += '<th>Case Number</th><th>Title</th><th>Type</th><th>Status</th><th>Judge</th><th>Action</th>';
    html += '</tr></thead><tbody>';

    data.forEach(caseItem => {
        html += `<tr>
            <td>${caseItem.case_number}</td>
            <td>${caseItem.case_title}</td>
            <td><span class="badge badge-secondary">${caseItem.case_type}</span></td>
            <td><span class="badge badge-${caseItem.status.toLowerCase().replace(' ', '-')}">${caseItem.status}</span></td>
            <td>${caseItem.judge_name || 'Unassigned'}</td>
            <td><a href="/admin/case/${caseItem.case_id}" class="btn btn-sm btn-info">View</a></td>
        </tr>`;
    });

    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
}

// Print functionality
function printPage() {
    window.print();
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    const csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push(col.innerText);
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename || 'export.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

// Initialize tooltips (if needed)
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
    console.log('Judicial Case Management System loaded');
});

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;

    switch(strength) {
        case 0:
        case 1:
        case 2:
            return 'Weak';
        case 3:
        case 4:
            return 'Medium';
        case 5:
            return 'Strong';
        default:
            return 'Weak';
    }
}

// Debounce function for search optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to search
const debouncedSearch = debounce((searchInputId, tableId) => {
    searchTable(searchInputId, tableId);
}, 300);