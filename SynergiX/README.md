# SynergiX Smart Contracts

Welcome to the **SynergiX** smart contracts repository! This project comprises two primary upgradeable smart contracts:

1. **SynergiXToken (`SynergiXToken`)**: An ERC20 token with staking, access control, and upgradeability features.
2. **SynergiXStaking (`SynergiXStaking`)**: A staking contract that manages token staking, referrals, and reward distributions.

This README is designed to guide new Solidity developers through setting up, testing, and deploying the SynergiX contracts effectively and securely.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [Compilation](#compilation)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Interacting with Contracts](#interacting-with-contracts)
10. [Upgradeability](#upgradeability)
11. [Security Best Practices](#security-best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)

---

## Project Overview

**SynergiX** is a decentralized platform that offers token staking services with a robust referral system. The ecosystem is powered by two interconnected smart contracts:

1. **SynergiXToken**: An ERC20 token that integrates staking functionalities, role-based access control, and upgradeability through the UUPS (Universal Upgradeable Proxy Standard) pattern.
2. **SynergiXStaking**: A staking contract that allows users to stake SynergiXTokens, earn rewards, and participate in a secure referral program.

Both contracts are designed to be upgradeable, ensuring future enhancements without altering their deployed addresses.

---

## Prerequisites

Before diving into the project, ensure you have the following tools and dependencies installed:

- **Node.js** (v14 or higher)
- **npm** (v6 or higher) or **yarn**
- **Git**
- **Hardhat**: A development environment for Ethereum software
- **OpenZeppelin Contracts**: Standardized smart contract libraries
- **Ethers.js**: A library for interacting with the Ethereum blockchain

### Installing Node.js and npm

Download and install Node.js from the [official website](https://nodejs.org/). This will also install npm.

```bash
# Verify installations
node -v
npm -v
```

### Installing Hardhat

```bash
# Install Hardhat globally
npm install --save-dev hardhat
```

### Cloning the Repository

```bash
git clone https://github.com/yourusername/SynergiX.git
cd SynergiX
```

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/SynergiX.git
   cd SynergiX
   ```

2. **Install Dependencies**

   Use either `npm` or `yarn` to install the required packages.

   ```bash
   # Using npm
   npm install
   
   # Using yarn
   yarn install
   ```

   This will install all necessary packages, including Hardhat, OpenZeppelin Contracts, and Ethers.js.

---

## Project Structure

Here's an overview of the project's directory structure:

```
SynergiX/
├── contracts/
│   ├── SynergiXToken.sol
│   ├── SynergiXStaking.sol
│   └── ISynergiXStaking.sol
├── scripts/
│   └── SynergixDeployment.js
├── test/
│   ├── SynergiXToken.test.js
│   └── SynergiXStaking.test.js
├── hardhat.config.js
├── package.json
└── README.md
```

- **contracts/**: Contains all Solidity smart contracts.
- **scripts/**: Deployment scripts for deploying contracts to the blockchain.
- **test/**: Test suites for verifying contract functionalities.
- **hardhat.config.js**: Configuration file for Hardhat.
- **package.json**: Project metadata and dependencies.
- **README.md**: Project documentation (this file).

---

## Configuration

### Setting Up Environment Variables

Create a `.env` file in the root directory to store sensitive information like private keys and API URLs. This file should **never** be committed to version control.

```bash
touch .env
```

Add the following variables to `.env`:

```dotenv
# .env
INFURA_PROJECT_ID=your_infura_project_id
PRIVATE_KEY=your_private_key
ADMIN_ADDRESS=0xYourAdminAddress
```

**Note:** Replace `your_infura_project_id`, `your_private_key`, and `0xYourAdminAddress` with your actual Infura project ID, private key, and admin Ethereum address, respectively.

### Updating Hardhat Configuration

Modify the `hardhat.config.js` file to include the necessary network configurations and plugins.

```javascript
// hardhat.config.js

require("@nomiclabs/hardhat-ethers");
require("@openzeppelin/hardhat-upgrades");
require("dotenv").config();

module.exports = {
    solidity: "0.8.0",
    networks: {
        rinkeby: {
            url: `https://rinkeby.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
            accounts: [`0x${process.env.PRIVATE_KEY}`]
        },
        mainnet: {
            url: `https://mainnet.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
            accounts: [`0x${process.env.PRIVATE_KEY}`]
        }
        // Add other networks as needed
    }
};
```

---

## Compilation

Compile the smart contracts using Hardhat to ensure there are no syntax errors and all dependencies are correctly resolved.

```bash
npx hardhat compile
```

If the compilation is successful, you'll see output similar to:

```
Compiled 2 Solidity files successfully
```

---

## Testing

Thoroughly test your smart contracts to ensure they behave as expected. Tests are written using Hardhat's testing framework with Mocha and Chai.

### Writing Tests

Navigate to the `test/` directory and create test files for each contract. Here's an example structure:

```javascript
// test/SynergiXToken.test.js

const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("SynergiXToken", function () {
    let Token, token, owner, addr1, addr2, staking;

    beforeEach(async function () {
        [owner, addr1, addr2, staking] = await ethers.getSigners();

        // Deploy SynergiXStaking as a proxy
        Token = await ethers.getContractFactory("SynergiXToken");
        token = await upgrades.deployProxy(Token, [owner.address, staking.address], { initializer: 'initialize' });
        await token.deployed();
    });

    it("Should have correct name and symbol", async function () {
        expect(await token.name()).to.equal("SynergiX Token");
        expect(await token.symbol()).to.equal("SNX");
    });

    it("Should assign ADMIN_ROLE to owner", async function () {
        const ADMIN_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("ADMIN_ROLE"));
        expect(await token.hasRole(ADMIN_ROLE, owner.address)).to.be.true;
    });

    // Add more tests covering all functionalities
});
```

### Running Tests

Execute the test suites using the following command:

```bash
npx hardhat test
```

Upon successful execution, you'll see detailed output of each test case.

---

## Deployment

Deploying the SynergiX contracts involves deploying both `SynergiXStaking` and `SynergiXToken` as upgradeable proxies and setting up the necessary roles and permissions.

### Deployment Script Overview

The deployment script performs the following steps:

1. **Deploy SynergiXStaking** as an upgradeable proxy.
2. **Deploy SynergiXToken** as an upgradeable proxy, initializing it with the admin and staking contract addresses.
3. **Assign the STAKING_ROLE** in `SynergiXToken` to the `SynergiXStaking` contract.

### Detailed Deployment Steps

1. **Ensure All Contracts Are Compiled**

   ```bash
   npx hardhat compile
   ```

2. **Run the Deployment Script**

   Execute the deployment script located at `scripts/SynergixDeployment.js`:

   ```bash
   npx hardhat run scripts/SynergixDeployment.js --network rinkeby
   ```

   **Replace `rinkeby`** with your desired network.

3. **Sample Deployment Script**

   Here's the fully updated and optimized `SynergixDeployment.js` script:

   ```javascript
   // scripts/SynergixDeployment.js

   const { ethers, upgrades } = require("hardhat");
   require("dotenv").config();

   async function main() {
       // Retrieve signers
       const [deployer] = await ethers.getSigners();

       console.log("Deploying contracts with the account:", deployer.address);
       console.log("Account balance:", (await deployer.getBalance()).toString());

       // Deploy SynergiXStaking as an upgradeable proxy
       const SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
       console.log("Deploying SynergiXStaking...");
       const staking = await upgrades.deployProxy(SynergiXStaking, [ethers.constants.AddressZero], { initializer: 'initialize' });
       await staking.deployed();
       console.log("SynergiXStaking deployed to:", staking.address);

       // Deploy SynergiXToken as an upgradeable proxy, initializing it with admin and staking address
       const SynergiXToken = await ethers.getContractFactory("SynergiXToken");
       console.log("Deploying SynergiXToken...");
       const token = await upgrades.deployProxy(SynergiXToken, [deployer.address, staking.address], { initializer: 'initialize' });
       await token.deployed();
       console.log("SynergiXToken deployed to:", token.address);

       // Assign the STAKING_ROLE in SynergiXToken to SynergiXStaking
       const STAKING_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("STAKING_ROLE"));
       const grantRoleTx = await token.grantRole(STAKING_ROLE, staking.address);
       await grantRoleTx.wait();
       console.log(`Granted STAKING_ROLE to SynergiXStaking (${staking.address}) in SynergiXToken.`);

       // Optionally, add SynergiXToken as a trusted contract in SynergiXStaking
       // If SynergiXStaking has a function to add trusted contracts
       // Example:
       // const addTrustedTx = await staking.addTrustedContract(token.address);
       // await addTrustedTx.wait();
       // console.log(`Added SynergiXToken (${token.address}) as a trusted contract in SynergiXStaking.`);
   }

   main()
       .then(() => process.exit(0))
       .catch(error => {
           console.error("Deployment failed:", error);
           process.exit(1);
       });
   ```

   ### **Key Points:**

   - **Upgradeable Proxies:** Both contracts are deployed as upgradeable proxies using OpenZeppelin's Upgrades plugin.
   - **Initialization Order:** `SynergiXStaking` is deployed first with a placeholder (`AddressZero`) for the token address, which is set during the deployment of `SynergiXToken`.
   - **Role Assignment:** After deploying both contracts, the `STAKING_ROLE` is granted to the `SynergiXStaking` contract within `SynergiXToken`.
   - **Logging:** The script logs critical information, such as contract addresses and role assignments, for easy tracking.

4. **Verify Deployment**

   After deployment, verify the contract addresses and role assignments:

   ```bash
   # Example output
   Deploying contracts with the account: 0xYourDeployerAddress
   Account balance: 100000000000000000000
   Deploying SynergiXStaking...
   SynergiXStaking deployed to: 0xStakingContractAddress
   Deploying SynergiXToken...
   SynergiXToken deployed to: 0xTokenContractAddress
   Granted STAKING_ROLE to SynergiXStaking (0xStakingContractAddress) in SynergiXToken.
   ```

---

## Interacting with Contracts

Once deployed, you can interact with the SynergiX contracts using scripts, Hardhat console, or frontend applications.

### Using Hardhat Console

Start the Hardhat console connected to your desired network:

```bash
npx hardhat console --network rinkeby
```

### Example Interactions

```javascript
const [owner, addr1] = await ethers.getSigners();

// Fetch deployed contract instances
const SynergiXToken = await ethers.getContractAt("SynergiXToken", "0xTokenContractAddress");
const SynergiXStaking = await ethers.getContractAt("SynergiXStaking", "0xStakingContractAddress");

// Approve tokens for staking
const stakeAmount = ethers.utils.parseEther("1000");
await SynergiXToken.connect(addr1).approve(SynergiXStaking.address, stakeAmount);

// Start a stake
const stakeDays = 30;
const tx = await SynergiXStaking.connect(owner).stakeStart(stakeAmount, stakeDays, addr1.address);
await tx.wait();

// End a stake
const stakeIndex = 0;
const endTx = await SynergiXStaking.connect(owner).stakeEnd(stakeIndex, addr1.address);
await endTx.wait();
```

---

## Upgradeability

Both `SynergiXToken` and `SynergiXStaking` contracts are designed to be upgradeable using the UUPS proxy pattern. This allows you to implement future enhancements without changing the contract addresses.

### Upgrading Contracts

1. **Modify the Contract Code**

   Make the necessary changes to the Solidity contract files in the `contracts/` directory.

2. **Compile the Contracts**

   ```bash
   npx hardhat compile
   ```

3. **Run the Upgrade Script**

   Create a new deployment script for the upgrade or modify the existing one.

   ```javascript
   // scripts/UpgradeSynergixContracts.js

   const { ethers, upgrades } = require("hardhat");

   async function main() {
       const SynergiXToken = await ethers.getContractFactory("SynergiXToken");
       console.log("Upgrading SynergiXToken...");
       await upgrades.upgradeProxy("0xTokenContractAddress", SynergiXToken);
       console.log("SynergiXToken upgraded successfully!");

       const SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
       console.log("Upgrading SynergiXStaking...");
       await upgrades.upgradeProxy("0xStakingContractAddress", SynergiXStaking);
       console.log("SynergiXStaking upgraded successfully!");
   }

   main()
       .then(() => process.exit(0))
       .catch(error => {
           console.error("Upgrade failed:", error);
           process.exit(1);
       });
   ```

   Run the upgrade script:

   ```bash
   npx hardhat run scripts/UpgradeSynergixContracts.js --network rinkeby
   ```

### Important Considerations

- **Storage Layout:** Ensure that the storage layout remains consistent between contract versions to prevent storage collisions.
- **Access Control:** Only accounts with the `ADMIN_ROLE` should perform upgrades to maintain security.
- **Testing Upgrades:** Thoroughly test upgrades on test networks before applying them to the mainnet.

---

## Upgradeability (Alternative Approach)

Alternatively, you can implement the upgrade within the existing contracts by adding setter functions to update the token address in the staking contract or vice versa. However, the UUPS proxy pattern with separate deployment provides a cleaner and more maintainable approach.

---

## Security Best Practices

Ensuring the security of your smart contracts is paramount. Here are some best practices to follow:

1. **Thorough Testing:**
   - Write comprehensive unit and integration tests covering all functionalities.
   - Use tools like [Hardhat](https://hardhat.org/), [Mocha](https://mochajs.org/), and [Chai](https://www.chaijs.com/) for testing.

2. **Code Audits:**
   - Before deploying to the mainnet, have your contracts audited by reputable security firms.
   - Address all vulnerabilities identified during audits.

3. **Access Control:**
   - Implement strict role-based access controls using OpenZeppelin's `AccessControl`.
   - Regularly review and update roles and permissions.

4. **Avoid Reentrancy:**
   - Use OpenZeppelin's `ReentrancyGuard` to protect against reentrancy attacks.
   - Follow the Checks-Effects-Interactions pattern.

5. **Limit Gas Consumption:**
   - Optimize gas usage by minimizing storage reads/writes and avoiding gas-intensive operations.
   - Use events for logging instead of storage variables when possible.

6. **Handle Edge Cases:**
   - Validate all inputs and handle unexpected scenarios gracefully.
   - Prevent integer overflows and underflows by using Solidity's built-in protections (>=0.8.0).

7. **Upgrade Safeguards:**
   - Restrict upgrade functionalities to trusted roles.
   - Ensure that upgraded contracts maintain the integrity and security of the system.

8. **Monitor Contracts:**
   - Use monitoring tools to track contract interactions and detect anomalies.
   - Implement fail-safes and emergency stop mechanisms if necessary.

---

## Troubleshooting

Here are some common issues you might encounter and how to resolve them:

1. **Compilation Errors:**
   - **Cause:** Syntax errors or incompatible Solidity versions.
   - **Solution:** Ensure all contracts use the same Solidity version specified in `hardhat.config.js`. Check for syntax mistakes.

2. **Deployment Failures:**
   - **Cause:** Insufficient gas, incorrect constructor parameters, or network issues.
   - **Solution:** Verify gas limits, ensure correct parameters are passed, and check network connectivity.

3. **Role Assignment Issues:**
   - **Cause:** Incorrect role hashes or missing role assignments.
   - **Solution:** Use `ethers.utils.keccak256` with `ethers.utils.toUtf8Bytes` to generate role hashes. Ensure roles are correctly granted.

4. **Reentrancy Errors:**
   - **Cause:** Functions vulnerable to reentrancy attacks.
   - **Solution:** Utilize `ReentrancyGuard` and follow the Checks-Effects-Interactions pattern.

5. **Upgrade Failures:**
   - **Cause:** Incompatible storage layouts or unauthorized upgrade attempts.
   - **Solution:** Ensure storage layout consistency and restrict upgrade functions to authorized roles.

6. **Transaction Reverts:**
   - **Cause:** Failed require statements or insufficient funds.
   - **Solution:** Review revert messages for clues. Ensure accounts have enough ETH for gas.

---

## Contributing

Contributions are welcome! To contribute to the SynergiX project, follow these steps:

1. **Fork the Repository**

   Click the "Fork" button at the top-right corner of this repository to create a personal copy.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/SynergiX.git
   cd SynergiX
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**

   Implement your feature or bug fix.

5. **Run Tests**

   Ensure all tests pass before committing.

   ```bash
   npx hardhat test
   ```

6. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

7. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**

   Navigate to the original repository and create a pull request from your fork.

### Contribution Guidelines

- **Follow Coding Standards:** Adhere to Solidity best practices and project-specific coding conventions.
- **Write Tests:** Ensure that new features are accompanied by comprehensive tests.
- **Document Your Code:** Provide clear comments and update the README as necessary.
- **Be Respectful:** Maintain a collaborative and respectful tone in all communications.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- **[OpenZeppelin](https://openzeppelin.com/)**: For providing secure and audited smart contract libraries.
- **[Hardhat](https://hardhat.org/)**: For the robust development environment.
- **[Ethers.js](https://docs.ethers.io/)**: For simplifying blockchain interactions.

---

## Final Thoughts

Congratulations on joining the SynergiX project! By following this guide, you'll be well-equipped to develop, test, and deploy the SynergiX smart contracts securely and efficiently. Always prioritize security, thorough testing, and adherence to best practices to maintain the integrity and reliability of the ecosystem.

Happy Coding! 🚀
