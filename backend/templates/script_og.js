const container = document.querySelector(".container");
const seats = document.querySelectorAll(".row .seat:not(.sold)");
const count = document.getElementById("count");
const total = document.getElementById("total");
const movieSelect = document.getElementById("movie");
const seatTaken=[];

document.addEventListener('DOMContentLoaded', function() {
  // All your code goes here
  function getQueryParam(name) {
      const urlParams = new URLSearchParams(window.location.search);
      return urlParams.get(name);
  }

  // Get the value of the 'screening_id' query parameter from URL
  const screeningId = getQueryParam('screening_id');

  // Display the screening ID on the page
  const screeningIdElement = document.getElementById('screeningId');
  screeningIdElement.innerText = 'Screening ID: ' + screeningId;

  function fetchScreeningData(screeningId) {
      fetch(`http://localhost:8000/screenings/seats/${screeningId}`)
      .then(response => response.json())
      .then(data => {
          console.log(data.data); // Log the data to console (for testing)
          // Display the fetched data on the page
            const seats = data.data.seats;
            const screeningDataElement = document.getElementById('screeningData');
            
        // Loop through each seat in the seats array
              seats.forEach(seat => {
            // Print the seat status
            if(seat.seat_status=="booked"){
              seatTaken.push(seat.seat_id);
              screeningDataElement.innerText+=seat.seat_id;
            }
            // screeningDataElement.innerText += `Seat ID: ${seat.seat_id}, Status: ${seat.seat_status} hi ` ;

        });
      })
      .catch(error => console.error('Error fetching screening data:', error));
  }
 
  // seatTaken.forEach(ticket=>{
  // screeningDataElement.innerText+=ticket
  // })
  // Call the fetchScreeningData function with the screening ID
  fetchScreeningData(screeningId);
});


seatTaken.forEach(ticket=>{
  screeningDataElement.innerText+=ticket+"hi"
})

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
  document.getElementById('totalInput').value = selectedSeatsCount * ticketPrice;

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