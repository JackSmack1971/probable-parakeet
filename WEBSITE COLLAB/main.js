function handleError(error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
} 

const registerUserForm = document.getElementById("register-user-form"); 

registerUserForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value; 

    if (isValidName(name) && isValidEmail(email)) {
        await registerUser(name, email);
    } else {
        alert("Please enter valid input.");
    }
}); 

const mineTokensForm = document.getElementById("mine-tokens-form"); 

mineTokensForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("email-for-mining").value;
    const proof = document.getElementById("proof").value; 

    if (isValidEmail(email) && isValidProof(proof)) {
        await mineTokens(email, proof);
    } else {
        alert("Please enter valid input.");
    }
}); 

const fetchNewsBtn = document.getElementById("fetch-news-btn");
const newsList = document.getElementById("news-list");
const loader = document.querySelector(".loader"); 

async function fetchNewsWithLoader() {
    loader.style.display = 'block'; // Show the loader
    const news = await fetchNews();
    loader.style.display = 'none'; // Hide the loader 

    // Clear the news list before appending new items
    newsList.innerHTML = '';
    news.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item.title;
        newsList.appendChild(li);
    });
} 

fetchNewsBtn.addEventListener("click", fetchNewsWithLoader); 

const fetchMiningDataBtn = document.getElementById("fetch-mining-data-btn");
const miningDataElem = document.getElementById("mining-data"); 

fetchMiningDataBtn.addEventListener("click", async () => {
    const miningData = await fetchMiningData();
    miningDataElem.textContent = JSON.stringify(miningData, null, 2);
});
