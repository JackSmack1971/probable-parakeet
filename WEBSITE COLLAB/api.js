// Add your WebSocket connection code here 

async function fetchData(url, method, body) {
    const response = await fetch(url, {
        method,
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    }); 

    if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
    } 

    return await response.json();
} 

async function registerUser(name, email) {
    try {
        const data = await fetchData("/register", "POST", { name, email });
        console.log(data);
    } catch (error) {
        handleError(error);
    }
} 

async function mineTokens(email, proof) {
    try {
        const data = await fetchData("/mine", "POST", { email, proof });
        console.log(data);
    } catch(error) {
        handleError(error);
    }
} 

async function fetchNews() {
    try {
        const data = await fetchData("/news", "GET");
        console.log(data);
        return data;
    } catch (error) {
        handleError(error);
    }
} 

async function fetchMiningData() {
    try {
        const data = await fetchData("/mining-data", "GET");
        console.log(data);
        return data;
    } catch (error) {
        handleError(error);
    }
}
