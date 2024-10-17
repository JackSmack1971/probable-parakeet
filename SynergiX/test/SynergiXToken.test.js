// test/SynergiXToken.test.js

const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("SynergiXToken", function () {
    let SynergiXStaking, synergiXStaking;
    let SynergiXToken, synergiXToken;
    let owner, admin, stakingOperator, user1, user2;

    const ADMIN_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("ADMIN_ROLE"));
    const STAKING_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("STAKING_ROLE"));
    const TRUSTED_CONTRACT_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("TRUSTED_CONTRACT_ROLE"));

    beforeEach(async function () {
        // Get signers
        [owner, admin, stakingOperator, user1, user2, ...addrs] = await ethers.getSigners();

        // Deploy SynergiXStaking as an upgradeable proxy
        SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
        synergiXStaking = await upgrades.deployProxy(SynergiXStaking, [owner.address], { initializer: 'initialize' });
        await synergiXStaking.deployed();

        // Deploy SynergiXToken as an upgradeable proxy, initializing with admin and staking contract address
        SynergiXToken = await ethers.getContractFactory("SynergiXToken");
        synergiXToken = await upgrades.deployProxy(SynergiXToken, [admin.address, synergiXStaking.address], { initializer: 'initialize' });
        await synergiXToken.deployed();

        // Assign STAKING_ROLE to SynergiXStaking contract
        await synergiXToken.grantRole(STAKING_ROLE, synergiXStaking.address);
    });

    describe("Deployment", function () {
        it("Should set the correct name and symbol", async function () {
            expect(await synergiXToken.name()).to.equal("SynergiX Token");
            expect(await synergiXToken.symbol()).to.equal("SNX");
        });

        it("Should assign ADMIN_ROLE to admin address", async function () {
            expect(await synergiXToken.hasRole(ADMIN_ROLE, admin.address)).to.equal(true);
        });

        it("Should assign STAKING_ROLE to SynergiXStaking contract", async function () {
            expect(await synergiXToken.hasRole(STAKING_ROLE, synergiXStaking.address)).to.equal(true);
        });

        it("Should have no initial tokens minted", async function () {
            const totalSupply = await synergiXToken.totalSupply();
            expect(totalSupply).to.equal(0);
        });
    });

    describe("Minting", function () {
        it("Should allow STAKING_ROLE to mint tokens", async function () {
            const mintAmount = ethers.utils.parseEther("1000");
            await synergiXToken.connect(admin).mint(user1.address, mintAmount);
            const balance = await synergiXToken.balanceOf(user1.address);
            expect(balance).to.equal(mintAmount);
        });

        it("Should not allow non-STAKING_ROLE to mint tokens", async function () {
            const mintAmount = ethers.utils.parseEther("1000");
            await expect(
                synergiXToken.connect(user1).mint(user1.address, mintAmount)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${STAKING_ROLE}`
            );
        });
    });

    describe("Role Management", function () {
        it("Admin should be able to grant ADMIN_ROLE to another account", async function () {
            await synergiXToken.connect(admin).grantRole(ADMIN_ROLE, stakingOperator.address);
            expect(await synergiXToken.hasRole(ADMIN_ROLE, stakingOperator.address)).to.equal(true);
        });

        it("Admin should be able to revoke ADMIN_ROLE from an account", async function () {
            await synergiXToken.connect(admin).grantRole(ADMIN_ROLE, stakingOperator.address);
            expect(await synergiXToken.hasRole(ADMIN_ROLE, stakingOperator.address)).to.equal(true);
            await synergiXToken.connect(admin).revokeRole(ADMIN_ROLE, stakingOperator.address);
            expect(await synergiXToken.hasRole(ADMIN_ROLE, stakingOperator.address)).to.equal(false);
        });

        it("Non-admin should not be able to grant ADMIN_ROLE", async function () {
            await expect(
                synergiXToken.connect(user1).grantRole(ADMIN_ROLE, user2.address)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${ADMIN_ROLE}`
            );
        });
    });

    describe("Staking Operations via SynergiXToken", function () {
        beforeEach(async function () {
            // Assign STAKING_OPERATOR_ROLE to SynergiXToken contract
            const STAKING_OPERATOR_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("STAKING_OPERATOR_ROLE"));
            await synergiXStaking.grantRole(STAKING_OPERATOR_ROLE, synergiXToken.address);
        });

        it("Should allow a user to stake tokens", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 30;

            // Mint tokens to user1
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);

            // Approve SynergiXToken to spend user1's tokens
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake tokens
            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.emit(synergiXStaking, "StakeStarted")
             .withArgs(user1.address, stakeAmount, stakeDays, anyValue); // anyValue for stakeIndex

            // Verify stake count
            const stakeCount = await synergiXStaking.numStakes(user1.address);
            expect(stakeCount).to.equal(1);

            // Verify token balance
            const balance = await synergiXToken.balanceOf(user1.address);
            expect(balance).to.equal(0);
        });

        it("Should not allow staking more than MAX_STAKING_VALUE", async function () {
            const stakeAmount = ethers.utils.parseEther("100001"); // Assuming MAX_STAKING_VALUE is 100000
            const stakeDays = 30;

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.be.revertedWith("Stake value exceeds maximum limit");
        });

        it("Should not allow staking with invalid stake days", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 0; // Invalid

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.be.revertedWith("Invalid staking duration");
        });

        it("Should allow a user to end their stake and receive payout", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 1; // Minimal days for testing

            // Mint and approve
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake
            await synergiXToken.connect(user1).stake(stakeAmount, stakeDays);

            // Fast forward time by 1 day
            await ethers.provider.send("evm_increaseTime", [86400]); // 1 day
            await ethers.provider.send("evm_mine");

            // End stake
            await expect(
                synergiXToken.connect(user1).stakeEnd(0)
            ).to.emit(synergiXStaking, "StakeEnded")
             .withArgs(user1.address, 0, anyValue); // payout amount is dynamic

            // Verify stake value is zero
            const stakeInfo = await synergiXStaking.getStakeInfo(0, user1.address);
            expect(stakeInfo.stakeValue).to.equal(0);
        });

        it("Should not allow ending a stake before it ends", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 30;

            // Mint and approve
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake
            await synergiXToken.connect(user1).stake(stakeAmount, stakeDays);

            // Attempt to end stake immediately
            await expect(
                synergiXToken.connect(user1).stakeEnd(0)
            ).to.be.revertedWith("Stake has not ended yet.");
        });

        it("Should correctly handle referral rewards upon staking", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 30;

            // Mint and approve
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Set referrer for user1 as admin
            await synergiXStaking.connect(owner).setReferrer(user1.address, admin.address);

            // Stake
            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.emit(synergiXStaking, "ReferralRewarded")
             .withArgs(admin.address, user1.address, anyValue, anyValue); // referrerReward, referredReward

            // Verify admin's balance increased by referrerReward
            const adminBalance = await synergiXToken.balanceOf(admin.address);
            expect(adminBalance).to.be.gt(0);

            // Verify user1's balance increased by referredReward
            const user1Balance = await synergiXToken.balanceOf(user1.address);
            expect(user1Balance).to.be.gt(0);
        });

        it("Should prevent circular referrals", async function () {
            // Set user1's referrer as user2
            await synergiXStaking.connect(owner).setReferrer(user1.address, user2.address);

            // Attempt to set user2's referrer as user1 (creates a loop)
            await expect(
                synergiXStaking.connect(owner).setReferrer(user2.address, user1.address)
            ).to.be.revertedWith("Circular referrer relationship detected.");
        });
    });

    describe("Upgradeability", function () {
        it("Should upgrade the contract correctly", async function () {
            // Assuming a new version with an additional function `version()`

            // Define a new contract version
            const SynergiXTokenV2 = await ethers.getContractFactory("SynergiXTokenV2"); // Ensure this contract exists
            synergiXToken = await upgrades.upgradeProxy(synergiXToken.address, SynergiXTokenV2);

            // Verify that the new function exists
            expect(await synergiXToken.version()).to.equal("v2");
        });
    });
});

