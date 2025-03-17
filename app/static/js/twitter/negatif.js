document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");

    const btnNavbarNotification = document.getElementById("btnNavbarNotification");
    let updateCounter = 0;
    const tbody = document.getElementById("datatablesSimple").getElementsByTagName("tbody")[0];

    function updateTable(data) {
        if (data.status === 'success') {
            const tweetsArray = Array.isArray(data.result_data) ? data.result_data : [];
            tweetsArray.sort((a, b) => a.grade - b.grade);
            const negativeTweets = tweetsArray.filter(tweet => tweet.sentimen === 'Negatif');
            // Bersihkan isi tbody sebelum mengisi dengan data baru
            tbody.innerHTML = '';

            if (negativeTweets.length > 0) {
                // Loop melalui setiap tweet dalam data
                negativeTweets.forEach(tweet => {
                    // Buat elemen <tr> untuk setiap tweet
                    const row = document.createElement("tr");

                    // Buat elemen <td> untuk created_at
                    const created_atCell = document.createElement("td");
                    const formattedDate = new Date(tweet.created_at).toLocaleDateString();
                    created_atCell.textContent = formattedDate;
                    row.appendChild(created_atCell);

                    // Buat elemen <td> untuk full_text
                    const textCell = document.createElement("td");
                    textCell.textContent = tweet.full_text;
                    row.appendChild(textCell);

                    // Buat elemen <td> untuk sentimen
                    const sentimenCell = document.createElement("td");
                    sentimenCell.textContent = tweet.sentimen;
                    row.appendChild(sentimenCell);

                    const gradeCell = document.createElement("td");
                    gradeCell.textContent = tweet.grade;
                    row.appendChild(gradeCell);

                    // Buat elemen <td> untuk tweet_url
                    const tweetUrlCell = document.createElement("td");
                    tweetUrlCell.innerHTML = `<a href="${tweet.tweet_url}" target="_blank">${tweet.tweet_url}</a>`;
                    row.appendChild(tweetUrlCell);

                    const deleteCell = document.createElement("td");
                    const deleteButton = document.createElement("button");
                    deleteButton.className = "btn btn-danger";
                    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
                    deleteButton.onclick = function() {
                        deleteData(tweet._id);
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

                const negativeNotificationTweets = tweetsArray
                    .filter(tweet => tweet.sentimen === 'Negatif')
                    .sort((a, b) => a.grade - b.grade) // Mengurutkan berdasarkan nilai sentimen
                    .slice(0, 5); // Mengambil 5 komentar teratas

                notificationDropdown.innerHTML = ''; // Bersihkan konten notifikasi

                negativeNotificationTweets.forEach(tweet => {
                    const notificationItem = document.createElement('li');
                    notificationItem.classList.add("d-flex", "align-items-center", "justify-content-between");
                    notificationItem.innerHTML = `
                        <span>
                            <a class="dropdown-item" href="${tweet.tweet_url}" target="_blank">${tweet.full_text}</a>
                        </span>
                        <span class="ms-2 d-flex align-items-center">
                            <button class="btn btn-sm btn-secondary me-2" onclick="window.open('${tweet.tweet_url}', '_blank')">${tweet.grade}</button>
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
                console.error('Error processing tweets: Empty negativeTweets array');
            }
        } else {
            console.error('Error processing tweets:', data.status);
        }
    }
    
    function deleteData(id) {
        fetch(`/delete_tweet_data/${id}`, {
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
        fetch('/data')
            .then(response => response.json())
            .then(data => {
                console.log("Data from /data:", data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    getData();

    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");

    function searchTweets(query) {
        fetch(`/search_tweets?q=${query}`)
            .then(response => response.json())
            .then(data => {
                console.log("Search result data:", data);
                updateTable(data);
            })
            .catch(error => {
                console.error('Error searching tweets:', error);
            });
    }

    // Event listener untuk tombol search
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim().toLowerCase();
        if (query !== '') {
            searchTweets(query);
        }
    });

    // Event listener untuk input search ketika menekan Enter
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim().toLowerCase();
            if (query !== '') {
                searchTweets(query);
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
