document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector(".container");
    const seats = document.querySelectorAll(".row .seat:not(.sold)");
    const count = document.getElementById("count");
    const total = document.getElementById("total");
    const movieSelect = document.getElementById("movie");
    const seatTaken = [];

    // Function to get query parameter from URL

    // Function to fetch screening data from the server
    function fetchScreeningData(screeningId) {
        console.log(screeningId)
        fetch(`http://127.0.0.1:5000/screenings/seats/1`)
            .then(response => response.json())
            .then(data => {
                console.log(data.data); // Log the data to console (for testing)
                return data.data.seats;
            })
            .catch(error => {
                console.error('Error fetching screening data:', error);
                return []; // Return an empty array in case of error
            });
    }

    // Function to update UI based on fetched data
    function updateUI(seats) {

        seats.forEach(seat => {

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
        });

        // Call other functions that depend on the fetched data
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

        const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));

        localStorage.setItem("selectedSeats", JSON.stringify(seatsIndex));

        const selectedSeatsCount = selectedSeats.length;

        count.innerText = selectedSeatsCount;
        total.innerText = selectedSeatsCount * ticketPrice;

        setMovieData(movieSelect.selectedIndex, movieSelect.value);
    }

    // Get the value of the 'screening_id' query parameter from URL
    const screeningId = getQueryParam('screening_id');

    // Display the screening ID on the page
    console.log(screeningId)
    // Call fetchScreeningData to fetch screening data
    fetchScreeningData(screeningId)
        .then(seats => {
            updateUI(seats); // Update UI with fetched data
        });

    // Event listener for movie select change
    movieSelect.addEventListener("change", (e) => {
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





const container = document.querySelector(".container");
const seats = document.querySelectorAll(".row .seat:not(.sold)");
const count = document.getElementById("count");
const total = document.getElementById("total");
const movieSelect = document.getElementById("movie");

populateUI();

let ticketPrice = +movieSelect.value;

// Save selected movie index and price
function setMovieData(movieIndex, moviePrice) {
  localStorage.setItem("selectedMovieIndex", movieIndex);
  localStorage.setItem("selectedMoviePrice", moviePrice);
}

// Update total and count
function updateSelectedCount() {
  const selectedSeats = document.querySelectorAll(".row .seat.selected");

  const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));

  localStorage.setItem("selectedSeats", JSON.stringify(seatsIndex));

  const selectedSeatsCount = selectedSeats.length;

  count.innerText = selectedSeatsCount;
  total.innerText = selectedSeatsCount * ticketPrice;

  setMovieData(movieSelect.selectedIndex, movieSelect.value);
}


// Get data from localstorage and populate UI
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
    console.log(selectedMovieIndex)
  }
}
console.log(populateUI())
// Movie select event
movieSelect.addEventListener("change", (e) => {
  ticketPrice = +e.target.value;
  setMovieData(e.target.selectedIndex, e.target.value);
  updateSelectedCount();
});

// Seat click event
container.addEventListener("click", (e) => {
  if (
    e.target.classList.contains("seat") &&
    !e.target.classList.contains("sold")
  ) {
    e.target.classList.toggle("selected");

    updateSelectedCount();
  }
});

// Initial count and total set
updateSelectedCount();