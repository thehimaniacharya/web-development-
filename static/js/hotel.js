let visible = 6;

function loadMore() {
    let cards = document.querySelectorAll(".hotel-card");
    for (let i = 0; i < visible + 6 && i < cards.length; i++) {
        cards[i].classList.remove("hidden");
    }
    visible += 6;
}

loadMore(); // initial load

function filterHotels() {
    let city = document.getElementById("cityFilter").value;
    let cards = document.querySelectorAll(".hotel-card");

    cards.forEach(card => {
        card.style.display =
            city === "all" || card.dataset.city === city ? "block" : "none";
    });
}

function sortHotels() {
    let grid = document.getElementById("hotelGrid");
    let cards = Array.from(grid.children);
    let type = document.getElementById("sortPrice").value;

    if (type === "default") return;

    cards.sort((a, b) => {
        return type === "low"
            ? a.dataset.price - b.dataset.price
            : b.dataset.price - a.dataset.price;
    });

    cards.forEach(card => grid.appendChild(card));
}
