document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");

    const btnNavbarNotification = document.getElementById("navbarDropdownNotification");
    const notificationDropdown = document.getElementById("notificationDropdown");
    let updateCounter = 0;
    const tbody = document.getElementById("datatablesSimple").getElementsByTagName("tbody")[0];

    function updateTable(data) {
        if (data.status === 'success') {
            const commentsArray = Array.isArray(data.result_data) ? data.result_data : [];
            commentsArray.sort((a, b) => a.grade - b.grade);
            // Filter to only show negative sentiment
            const negativeComments = commentsArray.filter(comment => comment.sentimen === 'Negatif');

            // Clear tbody before filling with new data
            tbody.innerHTML = '';

            if (negativeComments.length > 0) {
                // Loop through each comment in data
                negativeComments.forEach(comment => {
                    // Create <tr> element for each comment
                    const row = document.createElement("tr");

                    // Create <td> for Date
                    const dateCell = document.createElement("td");
                    dateCell.textContent = new Date(comment.Date).toLocaleDateString();
                    row.appendChild(dateCell); 

                    // Create <td> for Post URL
                    const urlCell = document.createElement("td");
                    urlCell.innerHTML = `<a href="${comment.URL}" target="_blank">${comment.URL}</a>`;
                    row.appendChild(urlCell);

                    // Create <td> for User
                    const userCell = document.createElement("td");
                    userCell.textContent = comment.Username || comment.User || 'N/A';
                    row.appendChild(userCell);

                    // Create <td> for Comment
                    const commentCell = document.createElement("td");
                    commentCell.textContent = comment.Comment;
                    row.appendChild(commentCell);

                    // Create <td> for Sentiment
                    const sentimenCell = document.createElement("td");
                    sentimenCell.textContent = comment.sentimen;
                    row.appendChild(sentimenCell);

                    // Create <td> for Grade
                    const gradeCell = document.createElement("td");
                    gradeCell.textContent = comment.grade;
                    row.appendChild(gradeCell);

                    // Create <td> for Delete Action
                    const deleteCell = document.createElement("td");
                    const deleteButton = document.createElement("button");
                    deleteButton.className = "btn btn-danger";
                    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
                    deleteButton.onclick = function() {
                        deleteData(comment._id);
                    };
                    deleteCell.appendChild(deleteButton);
                    row.appendChild(deleteCell);

                    // Add click event to highlight row based on sentiment
                    row.addEventListener('click', function() {
                        if (comment.sentimen === 'Negatif') {
                            row.classList.toggle('sentimen-negatif');
                        }
                    });

                    // Add row to table
                    tbody.appendChild(row);

                    // Increment update counter
                    updateCounter++;
                });

                // Prepare top 5 negative comments for notification dropdown
                const negativeNotificationComments = commentsArray
                    .filter(comment => comment.sentimen === 'Negatif')
                    .sort((a, b) => a.grade - b.grade)
                    .slice(0, 5);

                notificationDropdown.innerHTML = ''; // Clear notification content

                negativeNotificationComments.forEach(comment => {
                    const notificationItem = document.createElement('li');
                    notificationItem.classList.add("d-flex", "align-items-center", "justify-content-between");
                    notificationItem.innerHTML = `
                        <span>
                            <a class="dropdown-item" href="${comment.URL}" target="_blank">${comment.Comment}</a>
                        </span>
                        <span class="ms-2 d-flex align-items-center">
                            <button class="btn btn-sm btn-secondary me-2" onclick="window.open('${comment.URL}', '_blank')">${comment.grade}</button>
                        </span>
                    `;
                    notificationDropdown.appendChild(notificationItem);
                });

                // Show notification button if there are updates
                if (updateCounter > 0) {
                    btnNavbarNotification.style.display = 'block';
                } else {
                    btnNavbarNotification.style.display = 'none';
                }

            } else {
                console.error('Error processing comments: Empty negativeComments array');
            }
        } else {
            console.error('Error processing comments:', data.status);
        }
    }

    function deleteData(id) {
        fetch(`/delete_facebook_data/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                getData(); // Refresh data after delete
            } else {
                console.error('Error deleting data:', data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting data:', error);
        });
    }

    function getData() {
        fetch('/facebook_data')
            .then(response => response.json())
            .then(data => {
                console.log("Data from /facebook_data:", data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    // Initial data load
    getData();

    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");

    function searchFacebook(query) {
        fetch(`/search_facebook?q=${query}`)
            .then(response => response.json())
            .then(data => {
                console.log(`Search results for "${query}":`, data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error searching data:', error);
            });
    }
    
    // Search button event listener
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim().toLowerCase();
        if (query !== '') {
            searchFacebook(query);
        }
    });

    // Search input enter key event listener
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim().toLowerCase();
            if (query !== '') {
                searchFacebook(query);
            }
        }
    });

    // Refresh data every 3 minutes
    setInterval(getData, 180000);

    // Sidebar toggle functionality
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});