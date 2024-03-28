document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector(".container");
    const seats = document.querySelectorAll(".row .seat:not(.sold)");
    const count = document.getElementById("count");
    const total = document.getElementById("total");
    const movieSelect = document.getElementById("movie");
    const seatTaken = [];
    var dbSeats;
    var ticketSelected=[]

    // Function to fetch screening data from the server
    function fetchScreeningData(screeningId) {
        fetch(`http://localhost:5000/screenings/seats/${screeningId}`)
            .then(response => response.json())
            .then(data => {
                console.log("hi")
                console.log(data.data.seats); 
                dbSeats=data.data.seats;
                const screeningDataElement = document.getElementById('screeningData');
                screeningDataElement.innerText=data.data.seats;
                updateUI(seats,dbSeats)
                return data.data.seats;
            })
            .catch(error => {
                console.error('Error fetching screening data:', error);
                return [];
            });
    }
    
    // Function to update UI based on fetched data
    function updateUI(seats,dbSeats) {
        dbSeats.forEach(seat => {

            //if booked
            if (seat.seat_status === "booked") {
                seatTaken.push(seat.seat_id);
                const seatElement = document.getElementById(seat.seat_id);
                console.log(seatElement)    
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
            const seatElement = document.getElementById(seatId);
            if (seatElement) {
                seatElement.classList.add("sold");
            }
        });
    }

    // Call the function to style booked seats
    styleBookedSeats();

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
    }

    // Function to update selected count
    function updateSelectedCount() {
        const selectedSeats = document.querySelectorAll(".row .seat.selected");
        console.log()
        const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat)+1);

        localStorage.setItem("selectedSeats", JSON.stringify(seatsIndex));

        const selectedSeatsCount = selectedSeats.length;
        ticketPrice=15;
        count.innerText = selectedSeatsCount;
        total.innerText = selectedSeatsCount * ticketPrice;
        selectedSeats.push(seatsIndex)
    }


    // Call fetchScreeningData to fetch screening data
    const screeningIdElement = document.getElementById('screeningId').innerText;
    fetchScreeningData(screeningIdElement)

    // Event listener for seat click
    container.addEventListener("click", (e) => {
        if (e.target.classList.contains("seat") && !e.target.classList.contains("sold")) {
            e.target.classList.toggle("selected");
            updateSelectedCount();
        }
        
    }); 
    const paymentButton=document.getElementById("book-now");
        
    // Initial count and total set
    updateSelectedCount();

});