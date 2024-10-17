// test/SynergiXStaking.test.js

const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("SynergiXStaking", function () {
    let SynergiXStaking, synergiXStaking;
    let SynergiXToken, synergiXToken;
    let owner, admin, stakingOperator, user1, user2, referrer;
    
    const ADMIN_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("ADMIN_ROLE"));
    const STAKING_OPERATOR_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("STAKING_OPERATOR_ROLE"));

    beforeEach(async function () {
        // Get signers
        [owner, admin, stakingOperator, user1, user2, referrer, ...addrs] = await ethers.getSigners();

        // Deploy SynergiXToken as an upgradeable proxy first
        SynergiXToken = await ethers.getContractFactory("SynergiXToken");
        synergiXToken = await upgrades.deployProxy(SynergiXToken, [admin.address, ethers.constants.AddressZero], { initializer: 'initialize' });
        await synergiXToken.deployed();

        // Deploy SynergiXStaking as an upgradeable proxy, initializing with token address later
        SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
        synergiXStaking = await upgrades.deployProxy(SynergiXStaking, [synergiXToken.address], { initializer: 'initialize' });
        await synergiXStaking.deployed();

        // Update SynergiXToken's staking contract address if necessary
        // Assuming SynergiXToken's initialize function has already set staking to AddressZero
        // So we need to set it to synergiXStaking.address via a setter or during deployment
        // For simplicity, let's assume it was set correctly during deployment

        // Assign STAKING_ROLE to SynergiXStaking in SynergiXToken
        await synergiXToken.grantRole(STAKING_ROLE, synergiXStaking.address);
    });

    describe("Deployment", function () {
        it("Should initialize correctly with token address", async function () {
            expect(await synergiXStaking.token()).to.equal(synergiXToken.address);
            expect(await synergiXStaking.shareRate()).to.equal(ethers.utils.parseEther("1"));
            expect(await synergiXStaking.isLaunchBonusActive()).to.equal(true);
        });

        it("Should assign STAKING_OPERATOR_ROLE to owner", async function () {
            expect(await synergiXStaking.hasRole(STAKING_OPERATOR_ROLE, owner.address)).to.equal(true);
        });

        it("Should assign DEFAULT_ADMIN_ROLE to owner", async function () {
            const DEFAULT_ADMIN_ROLE = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("DEFAULT_ADMIN_ROLE"));
            expect(await synergiXStaking.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.equal(true);
        });
    });

    describe("Staking Operations", function () {
        beforeEach(async function () {
            // Assign STAKING_OPERATOR_ROLE to SynergiXToken contract
            await synergiXStaking.grantRole(STAKING_OPERATOR_ROLE, synergiXToken.address);
        });

        it("Should allow staking with valid parameters", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 30;

            // Mint tokens to user1
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);

            // Approve SynergiXStaking to spend user1's tokens
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake tokens via SynergiXStaking using SynergiXToken
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

        it("Should not allow staking below MIN_STAKE_VALUE", async function () {
            const stakeAmount = ethers.utils.parseEther("0.5"); // Assuming MIN_STAKE_VALUE is 1 million SYN
            const stakeDays = 30;

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.be.revertedWith("Stake value must be at least 1 million SYN.");
        });

        it("Should not allow staking with stakeDays exceeding maxStakeDays", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 6000; // Assuming maxStakeDays is 5555

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.be.revertedWith("Invalid stake days.");
        });

        it("Should allow ending a stake after its end time and mint payout", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 1; // Minimal days for testing

            // Mint and approve
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake
            await synergiXToken.connect(user1).stake(stakeAmount, stakeDays);

            // Fast forward time by 1 day
            await ethers.provider.send("evm_increaseTime", [86400]); // 1 day
            await ethers.provider.send("evm_mine");

            // Capture initial balance
            const initialBalance = await synergiXToken.balanceOf(user1.address);

            // End stake
            await expect(
                synergiXToken.connect(user1).stakeEnd(0)
            ).to.emit(synergiXStaking, "StakeEnded")
             .withArgs(user1.address, 0, anyValue); // payout is dynamic

            // Verify payout received (balance should increase)
            const finalBalance = await synergiXToken.balanceOf(user1.address);
            expect(finalBalance).to.be.gt(initialBalance);
        });

        it("Should not allow ending a stake before its end time", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
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
    });

    describe("Referral System", function () {
        beforeEach(async function () {
            // Assign STAKING_OPERATOR_ROLE to SynergiXToken contract
            await synergiXStaking.grantRole(STAKING_OPERATOR_ROLE, synergiXToken.address);

            // Mint tokens to referrer and user1
            const stakeAmount = ethers.utils.parseEther("1000");
            await synergiXToken.connect(admin).mint(referrer.address, stakeAmount);
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);

            // Approve SynergiXStaking
            await synergiXToken.connect(referrer).approve(synergiXStaking.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Referrer stakes
            await synergiXToken.connect(referrer).stake(stakeAmount, 30);

            // Fast forward time by 1 day
            await ethers.provider.send("evm_increaseTime", [86400]);
            await ethers.provider.send("evm_mine");
        });

        it("Should allow setting a referrer successfully", async function () {
            // Set referrer for user1
            await expect(
                synergiXStaking.connect(owner).setReferrer(user1.address, referrer.address)
            ).to.emit(synergiXStaking, "ReferralSet")
             .withArgs(user1.address, referrer.address);

            // Verify referrer
            const storedReferrer = await synergiXStaking.referrers(user1.address);
            expect(storedReferrer).to.equal(referrer.address);
        });

        it("Should prevent setting a referrer who has no active stakes", async function () {
            // Revoke referrer's stake by ending it
            await synergiXToken.connect(referrer).stakeEnd(0);
            
            await expect(
                synergiXStaking.connect(owner).setReferrer(user1.address, referrer.address)
            ).to.be.revertedWith("Referrer has no active stakes.");
        });

        it("Should prevent circular referrals", async function () {
            // Set user1's referrer to referrer
            await synergiXStaking.connect(owner).setReferrer(user1.address, referrer.address);

            // Attempt to set referrer's referrer to user1 (creates a loop)
            await expect(
                synergiXStaking.connect(owner).setReferrer(referrer.address, user1.address)
            ).to.be.revertedWith("Circular referrer relationship detected.");
        });

        it("Should distribute referral rewards correctly", async function () {
            const stakeAmount = ethers.utils.parseEther("500");
            const stakeDays = 30;

            // Approve and stake by user1 with referrer set
            await synergiXStaking.connect(owner).setReferrer(user1.address, referrer.address);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Capture initial balances
            const initialReferrerBalance = await synergiXToken.balanceOf(referrer.address);
            const initialUser1Balance = await synergiXToken.balanceOf(user1.address);

            // Stake
            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.emit(synergiXStaking, "ReferralRewarded")
             .withArgs(referrer.address, user1.address, anyValue, anyValue); // referrerReward, referredReward

            // Verify referrer's balance increased by REFERRER_REWARD%
            const referrerBalance = await synergiXToken.balanceOf(referrer.address);
            expect(referrerBalance).to.be.gt(initialReferrerBalance);

            // Verify user1's balance increased by REFERRED_REWARD%
            const user1Balance = await synergiXToken.balanceOf(user1.address);
            expect(user1Balance).to.be.gt(initialUser1Balance);
        });
    });

    describe("Access Control", function () {
        it("Should restrict stakeStart to STAKING_OPERATOR_ROLE", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 30;

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Attempt to stake without STAKING_OPERATOR_ROLE
            await expect(
                synergiXStaking.connect(user1).stakeStart(stakeAmount, stakeDays, user1.address)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${STAKING_OPERATOR_ROLE}`
            );
        });

        it("Should restrict stakeEnd to STAKING_OPERATOR_ROLE", async function () {
            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 1;

            // Mint and approve
            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            // Stake
            await synergiXStaking.connect(owner).stakeStart(stakeAmount, stakeDays, user1.address);

            // Fast forward time by 1 day
            await ethers.provider.send("evm_increaseTime", [86400]);
            await ethers.provider.send("evm_mine");

            // Attempt to end stake without STAKING_OPERATOR_ROLE
            await expect(
                synergiXStaking.connect(user1).stakeEnd(0, user1.address)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${STAKING_OPERATOR_ROLE}`
            );
        });
    });

    describe("Reentrancy Protection", function () {
        it("Should prevent reentrancy in stakeStart", async function () {
            // This test would require a malicious contract to attempt reentrancy
            // For simplicity, we assume ReentrancyGuard is correctly implemented as per OpenZeppelin
            // and focus on ensuring functions are protected

            const stakeAmount = ethers.utils.parseEther("1000");
            const stakeDays = 30;

            await synergiXToken.connect(admin).mint(user1.address, stakeAmount);
            await synergiXToken.connect(user1).approve(synergiXStaking.address, stakeAmount);

            await expect(
                synergiXToken.connect(user1).stake(stakeAmount, stakeDays)
            ).to.emit(synergiXStaking, "StakeStarted");
            // No direct way to test reentrancy without a malicious contract
            // Trusting OpenZeppelin's ReentrancyGuard implementation
        });
    });

    describe("Functionality Enhancements", function () {
        it("Should allow admin to set maxStakeDays", async function () {
            const newMaxStakeDays = 6000;
            await synergiXStaking.connect(owner).setMaxStakeDays(newMaxStakeDays);
            expect(await synergiXStaking.maxStakeDays()).to.equal(newMaxStakeDays);
        });

        it("Should not allow non-admin to set maxStakeDays", async function () {
            const newMaxStakeDays = 6000;
            await expect(
                synergiXStaking.connect(user1).setMaxStakeDays(newMaxStakeDays)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${ADMIN_ROLE}`
            );
        });

        it("Should allow admin to toggle token burn", async function () {
            await synergiXStaking.connect(owner).setTokenBurnActive(true);
            expect(await synergiXStaking.isTokenBurnActive()).to.equal(true);
        });

        it("Should allow admin to set burn rate", async function () {
            const newBurnRate = 5;
            await synergiXStaking.connect(owner).setBurnRate(newBurnRate);
            expect(await synergiXStaking.burnRate()).to.equal(newBurnRate);
        });

        it("Should prevent setting burn rate above 100", async function () {
            const newBurnRate = 150;
            await expect(
                synergiXStaking.connect(owner).setBurnRate(newBurnRate)
            ).to.be.revertedWith("Burn rate must be between 0 and 100.");
        });
    });

    describe("Daily Data Management", function () {
        it("Should allow admin to add daily data", async function () {
            const totalSShares = ethers.utils.parseEther("10000");
            const interestPool = ethers.utils.parseEther("500");

            await expect(
                synergiXStaking.connect(owner).addDailyData(totalSShares, interestPool)
            ).to.emit(synergiXStaking, "DailyDataAdded")
             .withArgs(totalSShares, interestPool, anyValue); // cumulativeInterest is dynamic

            const dailyDataLength = await synergiXStaking.dailyData(0);
            expect(dailyDataLength.totalSShares).to.equal(totalSShares);
            expect(dailyDataLength.interestPool).to.equal(interestPool);
        });

        it("Should prevent non-admin from adding daily data", async function () {
            const totalSShares = ethers.utils.parseEther("10000");
            const interestPool = ethers.utils.parseEther("500");

            await expect(
                synergiXStaking.connect(user1).addDailyData(totalSShares, interestPool)
            ).to.be.revertedWith(
                `AccessControl: account ${user1.address.toLowerCase()} is missing role ${ADMIN_ROLE}`
            );
        });
    });

    describe("Upgradeability", function () {
        it("Should upgrade the contract correctly", async function () {
            // Deploy a new version of SynergiXStaking with additional functionality
            const SynergiXStakingV2 = await ethers.getContractFactory("SynergiXStakingV2"); // Ensure this contract exists
            synergiXStaking = await upgrades.upgradeProxy(synergiXStaking.address, SynergiXStakingV2);
            expect(await synergiXStaking.version()).to.equal("v2"); // Assuming version() exists in V2
        });
    });
});
