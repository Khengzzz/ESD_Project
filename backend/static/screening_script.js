document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector(".container");
    const seats = document.querySelectorAll(".row .seat:not(.sold)");
    const count = document.getElementById("count");
    const total = document.getElementById("total");
    const movieSelect = document.getElementById("movie");
    const seatTaken = [];
    var dbSeats;




    // Function to fetch screening data from the server
    function fetchScreeningData(screeningId) {
        fetch(`http://localhost:5000/screenings/seats/${screeningId}`)
            .then(response => response.json())
            .then(data => {
                console.log("hi")
                console.log(data.data.seats); 
                dbSeats=data.data.seats;// Log the data to console (for testing)
                const screeningDataElement = document.getElementById('screeningData');
                screeningDataElement.innerText=data.data.seats;
                updateUI(dbSeats)
                return data.data.seats;
            })
            .catch(error => {
                console.error('Error fetching screening data:', error);
                return []; // Return an empty array in case of error
            });
    }
    
    // Function to update UI based on fetched data
    function updateUI(seats,dbSeats) {
        console.log("this is update ui")

       dbSeats.forEach(seat => {

            //if booked
            if (seat.seat_status === "booked") {
                seatTaken.push(seat.seat_id);
                const seatElement = document.getElementById(seat.seat_id);
                if (seatElement) {
                    seatElement.classList.add("sold"); 
                }
            }
            //if reserved 
            if (seat.seat_status === "reserved") {
                seatTaken.push(seat.seat_id);
                const seatElement = document.getElementById(seat.seat_id); 
                if (seatElement) {
                    seatElement.classList.add("reserved"); 
                }
            }
            document.getElementById("taken").textContent=seatTaken
            
        });

        // Call other functions that depend on the fetched data
        console.log("hi2")
        populateUI();
        updateSelectedCount();
    }
    //blockout seats
    function styleBookedSeats() {
        seatTaken.forEach(seatId => {
            const seatElement = document.getElementById(seatId); // Assuming seat IDs are prefixed with "seat"
            if (seatElement) {
                seatElement.classList.add("sold"); // Add the .booked class
            }
        });
       
    }

    // Call the function to style booked seats
    styleBookedSeats();

    let ticketPrice = +movieSelect.value;
    // Function to populate UI from local storage
    function populateUI() {
        const selectedSeats = JSON.parse(localStorage.getItem("selectedSeats"));
        
        if (selectedSeats !== null && selectedSeats.length > 0) {
            seats.forEach((seat, index) => {
                if (selectedSeats.indexOf(index) > -1) {
                    console.log(seat.classList.add("selected"));
                }
            });
        }

        const selectedMovieIndex = localStorage.getItem("selectedMovieIndex");

        if (selectedMovieIndex !== null) {
            movieSelect.selectedIndex = selectedMovieIndex;
            console.log(selectedMovieIndex);
        }
    }

    // Function to update selected count
    function updateSelectedCount() {
        const selectedSeats = document.querySelectorAll(".row .seat.selected");
        console.log("h3")
        const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));

        localStorage.setItem("selectedSeats", JSON.stringify(seatsIndex));

        const selectedSeatsCount = selectedSeats.length;

        count.innerText = selectedSeatsCount;
        total.innerText = selectedSeatsCount * ticketPrice;

        setMovieData(movieSelect.selectedIndex, movieSelect.value);
    }

    const screeningIdElement = document.getElementById('screeningId').innerText;
   

    // Call fetchScreeningData to fetch screening data
    
    fetchScreeningData(screeningIdElement)
    console.log(dbSeats)
    //  console.log(occupiedSeats)
    //     seats => {
    //         updateUI(seats); // Update UI with fetched data
    //     };

    // Event listener for movie select change
    movieSelect.addEventListener("change", (e) => {
        console.log("h4")
        ticketPrice = +e.target.value;
        setMovieData(e.target.selectedIndex, e.target.value);
        updateSelectedCount();
    });

    // Event listener for seat click
    container.addEventListener("click", (e) => {
        if (e.target.classList.contains("seat") && !e.target.classList.contains("sold")) {
            e.target.classList.toggle("selected");
            updateSelectedCount();
        }
    });

    // Initial count and total set
    updateSelectedCount();

    // Save selected movie index and price
    function setMovieData(movieIndex, moviePrice) {
        localStorage.setItem("selectedMovieIndex", movieIndex);
        localStorage.setItem("selectedMoviePrice", moviePrice);
    }
});