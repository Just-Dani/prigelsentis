document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");

    const btnNavbarNotification = document.getElementById("btnNavbarNotification");
    let updateCounter = 0;
    const tbody = document.getElementById("datatablesSimple").getElementsByTagName("tbody")[0];

    function updateTable(data) {
        if (data.status === 'success') {
            const commentsArray = Array.isArray(data.result_data) ? data.result_data : [];
            commentsArray.sort((a, b) => a.grade - b.grade);
            // Filter untuk hanya menampilkan sentimen positif
            const negativeComments = commentsArray.filter(comment => comment.sentimen === 'Negatif');

            // Bersihkan isi tbody sebelum mengisi dengan data baru
            tbody.innerHTML = '';

            if (negativeComments.length > 0) {
                // Loop melalui setiap komentar dalam data
                negativeComments.forEach(comment => {
                    // Buat elemen <tr> untuk setiap komentar
                    const row = document.createElement("tr");

                    // Buat elemen <td> untuk Date
                    const dateCell = document.createElement("td");
                    dateCell.textContent = new Date(comment.Date).toLocaleDateString();
                    row.appendChild(dateCell); 

                    // Buat elemen <td> untuk URL
                    const urlCell = document.createElement("td");
                    urlCell.innerHTML = `<a href="${comment.URL}" target="_blank">${comment.URL}</a>`;
                    row.appendChild(urlCell);

                    // Buat elemen <td> untuk Username
                    const usernameCell = document.createElement("td");
                    usernameCell.textContent = comment.Username;
                    row.appendChild(usernameCell);

                    // Buat elemen <td> untuk Comment
                    const commentCell = document.createElement("td");
                    commentCell.textContent = comment.Comment;
                    row.appendChild(commentCell);

                    const sentimenCell = document.createElement("td");
                    sentimenCell.textContent = comment.sentimen;
                    row.appendChild(sentimenCell);

                    // Buat elemen <td> untuk Grade
                    const gradeCell = document.createElement("td");
                    gradeCell.textContent = comment.grade;
                    row.appendChild(gradeCell);

                    const deleteCell = document.createElement("td");
                    const deleteButton = document.createElement("button");
                    deleteButton.className = "btn btn-danger";
                    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
                    deleteButton.onclick = function() {
                        deleteData(comment._id);
                    };
                    deleteCell.appendChild(deleteButton);
                    row.appendChild(deleteCell);

                    row.addEventListener('click', function() {
                        // Tambahkan kelas berdasarkan sentimen yang diklik
                        if (tweet.sentimen === 'Positif') {
                            row.classList.toggle('sentimen-positif');
                        } else if (tweet.sentimen === 'Netral') {
                            row.classList.toggle('sentimen-netral');
                        } else if (tweet.sentimen === 'Negatif') {
                            row.classList.toggle('sentimen-negatif');
                        }
                    });

                    // Tambahkan baris ke dalam tabel
                    tbody.appendChild(row);

                    // Tambahkan pembaharuan
                    updateCounter++;
                });

                const negativeNotificationComments = commentsArray
                    .filter(comment => comment.sentimen === 'Negatif')
                    .sort((a, b) => a.grade - b.grade) // Mengurutkan berdasarkan nilai sentimen
                    .slice(0, 5); // Mengambil 5 komentar teratas

                notificationDropdown.innerHTML = ''; // Bersihkan konten notifikasi

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

                // Jika ada pembaharuan, hidupkan tombol
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
        fetch(`/delete_instagram_data/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                getData(); // Refresh data setelah menghapus
            } else {
                console.error('Error deleting data:', data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting data:', error);
        });
    }

    function getData() {
        fetch('/instagram_data')
            .then(response => response.json())
            .then(data => {
                console.log("Data from /instagram_data:", data);  // Tambahkan log untuk data dari endpoint
                updateTable(data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    getData();

    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");

    function searchInstagram(query) {
        fetch(`/search_instagram?q=${query}`)
            .then(response => response.json())
            .then(data => {
                console.log(`Search results for "${query}":`, data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error searching data:', error);
            });
    }
    

    // Event listener untuk tombol search
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim().toLowerCase();
        if (query !== '') {
            searchInstagram(query);
        }
    });

    // Event listener untuk input search ketika menekan Enter
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim().toLowerCase();
            if (query !== '') {
                searchInstagram(query);
            }
        }
    });

    setInterval(getData, 180000); // Ambil data setiap 3 menit

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        // new simpleDatatables.DataTable(datatablesSimple, {
        //     lengthMenu: [5, 10, 15, [ -1, "All" ]],
        //     columns: [{
        //             select: 2,
        //             sortSequence: ["desc", "asc"]
        //         },
        //         {
        //             select: 3,
        //             sortSequence: ["asc"]
        //         },
        //         {
        //             select: 4,
        //             cellClass: "green",
        //             headerClass: "red"
        //         }
        //     ]
        // });
    }

    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});
