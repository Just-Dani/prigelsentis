// Initialize the Facebook dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load data for Facebook dashboard
    loadFacebookData();
    
    // Initialize search functionality
    document.getElementById('searchBtn').addEventListener('click', function() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        filterFacebookComments(searchTerm);
    });
});

function loadFacebookData() {
    // Here you would typically make an API call to your backend
    // For now, we'll use mock data
    const mockData = [
        {
            date: '2023-11-15',
            url: 'https://facebook.com/post/123',
            username: 'user1',
            comment: 'Great post!',
            sentiment: 'Positif'
        },
        {
            date: '2023-11-14',
            url: 'https://facebook.com/post/456',
            username: 'user2',
            comment: 'I think this is okay',
            sentiment: 'Netral'
        },
        {
            date: '2023-11-13',
            url: 'https://facebook.com/post/789',
            username: 'user3',
            comment: 'I disagree with this',
            sentiment: 'Negatif'
        }
    ];
    
    renderFacebookTable(mockData);
}

function renderFacebookTable(data) {
    const tableBody = document.querySelector('#datatablesSimple tbody');
    tableBody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${item.date}</td>
            <td><a href="${item.url}" target="_blank">View Post</a></td>
            <td>${item.username}</td>
            <td>${item.comment}</td>
            <td>${item.sentiment}</td>
            <td>
                <button class="btn btn-danger btn-sm delete-btn" data-id="${item.url}">Delete</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to delete buttons
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-id');
            deleteFacebookComment(postId);
        });
    });
}

function filterFacebookComments(searchTerm) {
    // Implement search functionality
    const rows = document.querySelectorAll('#datatablesSimple tbody tr');
    
    rows.forEach(row => {
        const comment = row.cells[3].textContent.toLowerCase();
        if (comment.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function deleteFacebookComment(postId) {
    // Here you would typically make an API call to delete the comment
    console.log(`Deleting Facebook comment with ID: ${postId}`);
    alert(`Comment from post ${postId} would be deleted (simulated)`);
}