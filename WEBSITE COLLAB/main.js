/* General styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
} 

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    background-color: #f4f4f4;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
} 

h1,
h2 {
    color: #333;
    margin-bottom: 20px;
} 

.container {
    max-width: 1170px;
    background-color: #fff;
    padding: 30px;
    box-shadow: 0 1px 15px rgba(0, 0, 0, 0.12), 0 1px 10px rgba(0, 0, 0, 0.24);
    border-radius: 10px;
    opacity: 0;
    transform: translateY(20px);
    animation: fadeIn 1s ease-out forwards;
} 

@keyframes fadeIn {
    100% {
        opacity: 1;
        transform: translateY(0);
    }
} 

/* Registration container */
#user-registration-container,
#token-mining-container,
#news-container,
#mining-data-container {
    margin-bottom: 20px;
} 

form {
    display: flex;
    flex-direction: column;
} 

label,
input {
    margin-bottom: 10px;
} 

input,
button {
    height: 40px;
    border-radius: 5px;
} 

input {
    transition: all 0.3s ease;
    border: 1px solid #ccc;
} 

input:focus,
input:hover {
    border-color: #1e88e5;
    box-shadow: 0 0 5px rgba(30, 136, 229, 0.5);
} 

button {
    background-color: #1e88e5;
    color: #fff;
    font-size: 18px;
    cursor: pointer;
    border: none;
    width: 50%;
    margin: 0 auto;
    transition: background-color 0.3s ease;
} 

button:hover {
    background-color: #1565c0;
} 

/* News container */
.news-item {
    margin-bottom: 10px;
    opacity: 0;
    transform: scaleY(0);
    transform-origin: top;
    animation: expand 0.5s ease-out forwards;
    animation-fill-mode: both;
} 

@keyframes expand {
    100% {
        opacity: 1;
        transform: scaleY(1);
    }
} 

.news-title {
    font-size: 18px;
    color: #333;
    margin-bottom: 5px;
} 

.news-source {
    font-size: 14px;
    color: #999;
} 

.news-item:nth-child(2) {
    animation-delay: 0.1s;
} 

.news-item:nth-child(3) {
    animation-delay: 0.2s;
} 

.news-item:nth-child(4) {
    animation-delay: 0.3s;
} 

/* Add more rules if there are more news items */ 

/* Loader */
.loader {
    border: 2px solid #f3f3f3;
    border-radius: 50%;
    border-top: 2px solid #1e88e5;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    display: none;
    margin: 0 auto;
} 

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
} 

/* Responsive styles */
@media (max-width: 768px) {
    .container {
        padding: 15px;
    } 

    button {
        width: 100%;
    }
}
