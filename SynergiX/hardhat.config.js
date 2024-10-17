require("@nomiclabs/hardhat-ethers");
require("@openzeppelin/hardhat-upgrades");

module.exports = {
    solidity: "0.8.0",
    networks: {
        rinkeby: {
            url: "https://rinkeby.infura.io/v3/YOUR_INFURA_PROJECT_ID",
            accounts: ["0xYourPrivateKey"]
        },
        mainnet: {
            url: "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
            accounts: ["0xYourPrivateKey"]
        }
        // Add other networks as needed
    }
};
