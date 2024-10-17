// scripts/SynergixDeployment.js

const { ethers, upgrades } = require("hardhat");

async function main() {
    // Replace with your admin address
    const admin = "0xYourAdminAddressHere";

    // Deploy SynergiXStaking as an upgradeable proxy
    const SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
    console.log("Deploying SynergiXStaking...");
    const staking = await upgrades.deployProxy(SynergiXStaking, [], { initializer: 'initialize' });
    await staking.deployed();
    console.log("SynergiXStaking deployed to:", staking.address);

    // Deploy SynergiXToken as an upgradeable proxy, initializing it with admin and staking address
    const SynergiXToken = await ethers.getContractFactory("SynergiXToken");
    console.log("Deploying SynergiXToken...");
    const token = await upgrades.deployProxy(SynergiXToken, [admin, staking.address], { initializer: 'initialize' });
    await token.deployed();
    console.log("SynergiXToken deployed to:", token.address);

    // Optionally, if SynergiXStaking needs to know the token address post-deployment,
    // you can implement and call a setter function in SynergiXStaking.
    // However, in this setup, SynergiXStaking receives the token address during initialization.

    // Assign the STAKING_ROLE in SynergiXToken to SynergiXStaking
    const STAKING_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("STAKING_ROLE"));
    const grantRoleTx = await token.grantRole(STAKING_ROLE, staking.address);
    await grantRoleTx.wait();
    console.log(`Granted STAKING_ROLE to SynergiXStaking (${staking.address}) in SynergiXToken.`);

    // Optionally, add SynergiXToken as a trusted contract in SynergiXStaking
    // If SynergiXStaking has a function to add trusted contracts
    // For example:
    // const addTrustedTx = await staking.addTrustedContract(token.address);
    // await addTrustedTx.wait();
    // console.log(`Added SynergiXToken (${token.address}) as a trusted contract in SynergiXStaking.`);

    // Verify the deployment (optional)
    // You can add verification steps here if deploying to a public network
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error("Deployment failed:", error);
        process.exit(1);
    });
