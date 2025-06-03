document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded (Facebook)");

    const btnNavbarNotification = document.getElementById("btnNavbarNotification");
    let updateCounter = 0;
    const tbody = document.getElementById("datatablesSimple").getElementsByTagName("tbody")[0];
    const notificationDropdown = document.getElementById("notificationDropdown");

    function updateTable(data) {
        if (data.status === 'success') {
            const commentsArray = Array.isArray(data.result_data) ? data.result_data : [];
            commentsArray.sort((a, b) => new Date(b.Date) - new Date(a.Date));

            tbody.innerHTML = '';

            if (commentsArray.length > 0) {
                commentsArray.forEach(comment => {
                    const row = document.createElement("tr");

                    const dateCell = document.createElement("td");
                    dateCell.textContent = new Date(comment.Date).toLocaleDateString();
                    row.appendChild(dateCell);

                    const urlCell = document.createElement("td");
                    urlCell.innerHTML = `<a href="${comment.URL}" target="_blank">${comment.URL}</a>`;
                    row.appendChild(urlCell);

                    const usernameCell = document.createElement("td");
                    usernameCell.textContent = comment.Username;
                    row.appendChild(usernameCell);

                    const commentCell = document.createElement("td");
                    commentCell.textContent = comment.Comment;
                    row.appendChild(commentCell);

                    const sentimenCell = document.createElement("td");
                    sentimenCell.textContent = comment.sentimen;
                    row.appendChild(sentimenCell);

                    const deleteCell = document.createElement("td");
                    const deleteButton = document.createElement("button");
                    deleteButton.className = "btn btn-danger";
                    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
                    deleteButton.onclick = function () {
                        deleteData(comment._id);
                    };
                    deleteCell.appendChild(deleteButton);
                    row.appendChild(deleteCell);

                    row.addEventListener('click', function () {
                        if (comment.sentimen === 'Positif') {
                            row.classList.toggle('sentimen-positif');
                        } else if (comment.sentimen === 'Netral') {
                            row.classList.toggle('sentimen-netral');
                        } else if (comment.sentimen === 'Negatif') {
                            row.classList.toggle('sentimen-negatif');
                        }
                    });

                    tbody.appendChild(row);
                    updateCounter++;
                });

                const negativeNotificationComments = commentsArray
                    .filter(comment => comment.sentimen === 'Negatif')
                    .sort((a, b) => a.grade - b.grade)
                    .slice(0, 5);

                notificationDropdown.innerHTML = '';

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

                btnNavbarNotification.style.display = updateCounter > 0 ? 'block' : 'none';

            } else {
                console.error('No Facebook comments found.');
            }
        } else {
            console.error('Error processing Facebook comments:', data.status);
        }
    }
    
    function deleteData(id) {
        fetch(`/delete_facebook_data/${id}`, {
            method: 'DELETE',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    getData(); // Refresh after deletion
                } else {
                    console.error('Error deleting Facebook data:', data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting Facebook data:', error);
            });
    }

    function getData() {
        fetch('/facebook_data')
            .then(response => response.json())
            .then(data => {
                console.log("Facebook data received:", data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error fetching Facebook data:', error);
            });
    }

    getData();

    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");

    function searchFacebook(query) {
        fetch(`/search_facebook?q=${query}`)
            .then(response => response.json())
            .then(data => {
                console.log(`Search results for "${query}" (Facebook):`, data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error searching Facebook data:', error);
            });
    }

    searchBtn.addEventListener('click', function () {
        const query = searchInput.value.trim().toLowerCase();
        if (query !== '') {
            searchFacebook(query);
        }
    });

    searchInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim().toLowerCase();
            if (query !== '') {
                searchFacebook(query);
            }
        }
    });

    setInterval(getData, 180000); // Refresh every 3 minutes

    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});
