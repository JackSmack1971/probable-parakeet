// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Import OpenZeppelin Contracts
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Burnable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./ISynergiXStaking.sol";

/// @title ISynergiXToken Interface
/// @notice Interface for the SynergiXToken Contract (mint function)
interface ISynergiXToken {
    function mint(address to, uint256 amount) external;
}

/// @title SynergiXStaking
/// @notice Staking Contract for SynergiXToken
contract SynergiXStaking is ISynergiXStaking, Ownable, AccessControl, ReentrancyGuard {
    // Roles Definitions
    bytes32 public constant STAKING_OPERATOR_ROLE = keccak256("STAKING_OPERATOR_ROLE");

    // Constants
    uint256 public constant MAX_STAKE_DAYS = 5555;
    uint256 public constant BONUS_MAX = 200; // Percentage
    uint256 public constant BONUS_MIN_STAKE = 150 * 10**6 * 10**18; // 150 million SYN (assuming 18 decimals)
    uint256 public constant MIN_STAKE_VALUE = 1 * 10**6 * 10**18; // 1 million SYN (assuming 18 decimals)

    // Referral System
    uint256 public constant REFERRER_REWARD = 2; // Percentage
    uint256 public constant REFERRED_REWARD = 1; // Percentage
    mapping(address => address) public referrers;

    // Data structures
    struct Stake {
        uint256 stakeValue;
        uint32 stakeDays;
        uint256 startTimestamp;
        uint256 endTimestamp;
        uint256 sShares;
    }

    struct DailyData {
        uint256 totalSShares;
        uint256 interestPool;
        uint256 cumulativeInterest;
    }

    // Variables
    ISynergiXToken public token;
    uint256 public shareRate;
    mapping(address => Stake[]) public stakes;
    DailyData[] public dailyData;

    // Sustainability Features
    uint32 public maxStakeDays = uint32(MAX_STAKE_DAYS);
    bool public isTokenBurnActive;
    uint256 public burnRate = 1; // Percentage

    // Tokenomics Features
    bool public isLaunchBonusActive;
    uint256 public launchBonusEndTimestamp;
    uint256 public launchBonusPercentage = 10; // Percentage

    // Events
    event StakeStarted(address indexed staker, uint256 stakeValue, uint32 stakeDays, uint256 sShares);
    event StakeEnded(address indexed staker, uint256 stakeIndex, uint256 payout);
    event ReferralRewarded(address indexed referrer, address indexed staker, uint256 referrerReward, uint256 referredReward);
    event ReferralSet(address indexed staker, address indexed referrer);
    event MaxStakeDaysUpdated(uint32 newMaxStakeDays);
    event TokenBurnStatusUpdated(bool isTokenBurnActive);
    event BurnRateUpdated(uint256 newBurnRate);
    event LaunchBonusStatusUpdated(bool isLaunchBonusActive);
    event LaunchBonusPercentageUpdated(uint256 newLaunchBonusPercentage);
    event LaunchBonusEndTimestampUpdated(uint256 newLaunchBonusEndTimestamp);
    event LaunchBonusToggled(bool isLaunchBonusActive);
    event DailyDataAdded(uint256 totalSShares, uint256 interestPool, uint256 cumulativeInterest);
    event ReferralInvalid(address indexed staker, address indexed referrer);

    /// @notice Constructor to initialize the staking contract
    /// @param _token The ERC20 token to be staked (SynergiXToken)
    constructor(ISynergiXToken _token) {
        require(address(_token) != address(0), "Token address cannot be zero");
        token = _token;
        shareRate = 1 * 10**18;
        isLaunchBonusActive = true;
        launchBonusEndTimestamp = block.timestamp + 30 days;

        // Grant the owner the default admin role: it will be able
        // to grant and revoke any roles
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(STAKING_OPERATOR_ROLE, msg.sender);
    }

    /// @notice Grants the STAKING_OPERATOR_ROLE to a specified account
    /// @param account The account to grant the role to
    function grantStakingOperator(address account) external onlyOwner {
        grantRole(STAKING_OPERATOR_ROLE, account);
    }

    /// @notice Revokes the STAKING_OPERATOR_ROLE from a specified account
    /// @param account The account to revoke the role from
    function revokeStakingOperator(address account) external onlyOwner {
        revokeRole(STAKING_OPERATOR_ROLE, account);
    }

    /// @notice Starts a new stake
    /// @param stakeValue The amount to stake
    /// @param stakeDays The duration of the stake in days
    /// @param staker The address of the staker
    /// @return stakeIndex The index of the newly created stake
    function stakeStart(uint256 stakeValue, uint256 stakeDays, address staker) external override onlyRole(STAKING_OPERATOR_ROLE) nonReentrant returns (uint256 stakeIndex) {
        require(stakeValue >= MIN_STAKE_VALUE, "Stake value must be at least 1 million SYN.");
        require(stakeDays > 0 && stakeDays <= maxStakeDays, "Invalid stake days.");

        // Transfer tokens from the staker to the staking contract
        bool success = token.transferFrom(staker, address(this), stakeValue);
        require(success, "Token transfer failed.");

        uint256 sShares = calcStakeShares(stakeValue, uint32(stakeDays));
        uint256 startTimestamp = block.timestamp;
        uint256 endTimestamp = startTimestamp + (stakeDays * 86400);

        stakes[staker].push(Stake({
            stakeValue: stakeValue,
            stakeDays: uint32(stakeDays),
            startTimestamp: startTimestamp,
            endTimestamp: endTimestamp,
            sShares: sShares
        }));

        stakeIndex = stakes[staker].length - 1;

        // Emit StakeStarted event
        emit StakeStarted(staker, stakeValue, uint32(stakeDays), sShares);

        // Reward referrals if applicable
        _rewardReferral(staker, stakeValue);
    }

    /// @notice Ends an active stake and handles payout
    /// @param stakeIndex The index of the stake to end
    /// @param staker The address of the staker
    function stakeEnd(uint256 stakeIndex, address staker) external override onlyRole(STAKING_OPERATOR_ROLE) nonReentrant {
        require(stakeIndex < stakes[staker].length, "Invalid stake index.");
        Stake storage userStake = stakes[staker][stakeIndex];
        require(block.timestamp >= userStake.endTimestamp, "Stake has not ended yet.");
        require(userStake.stakeValue > 0, "Stake has already been ended.");

        // Calculate payout
        uint256 payout = _calculatePayout(staker, stakeIndex);

        // Update the stake to indicate it has been ended
        userStake.stakeValue = 0;
        userStake.sShares = 0;

        // Burn tokens if the feature is active
        if (isTokenBurnActive) {
            uint256 burnAmount = (payout * burnRate) / 100;
            payout -= burnAmount;
            token.mint(address(this), burnAmount); // Mint burnAmount to this contract
            token.burn(burnAmount);
        }

        // Mint reward tokens to the staker
        token.mint(staker, payout);

        // Emit StakeEnded event
        emit StakeEnded(staker, stakeIndex, payout);
    }

    /// @notice Calculates the stake shares based on stake value and days
    /// @param stakeValue The value of the stake
    /// @param stakeDays The duration of the stake in days
    /// @return sShares The calculated stake shares
    function calcStakeShares(uint256 stakeValue, uint32 stakeDays) public view returns (uint256 sShares) {
        uint256 bonusMultiplier = (BONUS_MAX * (stakeDays - 1)) / (maxStakeDays - 1);
        uint256 bonus = 0;

        if (stakeValue >= BONUS_MIN_STAKE) {
            bonus = (stakeValue * bonusMultiplier) / 100;
        }

        uint256 effectiveValue = stakeValue + bonus;
        sShares = (effectiveValue * 10**18) / shareRate;
    }

    /// @notice Rewards referrers based on staking
    /// @param staker The address of the staker
    /// @param stakeValue The value of the stake
    function _rewardReferral(address staker, uint256 stakeValue) internal {
        address referrer = referrers[staker];
        if (referrer != address(0)) {
            uint256 referrerReward = (stakeValue * REFERRER_REWARD) / 100;
            uint256 referredReward = (stakeValue * REFERRED_REWARD) / 100;

            // Mint the referredReward to the staker
            token.mint(staker, referredReward);

            // Mint the referrerReward to the referrer
            token.mint(referrer, referrerReward);

            // Emit ReferralRewarded event
            emit ReferralRewarded(referrer, staker, referrerReward, referredReward);
        }
    }

    /// @notice Calculates the payout for a stake
    /// @param staker The address of the staker
    /// @param stakeIndex The index of the stake
    /// @return payout The calculated payout amount
    function _calculatePayout(address staker, uint256 stakeIndex) internal view returns (uint256 payout) {
        Stake storage stake = stakes[staker][stakeIndex];
        uint256 startDayIndex = stake.startTimestamp / 86400;
        uint256 endDayIndex = stake.endTimestamp / 86400;
        uint256 sShares = stake.sShares;

        require(endDayIndex < dailyData.length, "Invalid end day index.");

        uint256 totalCumulativeInterest = dailyData[endDayIndex].cumulativeInterest - dailyData[startDayIndex].cumulativeInterest;
        uint256 interest = (totalCumulativeInterest * sShares) / dailyData[endDayIndex].totalSShares;

        payout = stake.stakeValue + interest;
    }

    /// @notice Sets the referrer for the caller
    /// @param referrer The address of the referrer
    function setMyReferrer(address referrer) external nonReentrant {
        require(referrer != address(0), "Referrer cannot be zero address.");
        require(referrer != msg.sender, "Cannot refer yourself.");
        require(referrers[msg.sender] == address(0), "Referrer already set.");
        require(stakes[referrer].length > 0, "Referrer has no stakes.");

        // Check if the referrer has at least one active stake
        bool hasActiveStake = false;
        uint256 len = stakes[referrer].length;
        for (uint256 i = 0; i < len; i++) {
            if (block.timestamp < stakes[referrer][i].endTimestamp && stakes[referrer][i].stakeValue > 0) {
                hasActiveStake = true;
                break;
            }
        }
        require(hasActiveStake, "Referrer has no active stakes.");

        // Prevent circular referrals
        address currentReferrer = referrer;
        while (currentReferrer != address(0)) {
            if (currentReferrer == msg.sender) {
                revert("Circular referrer relationship detected.");
            }
            currentReferrer = referrers[currentReferrer];
        }

        referrers[msg.sender] = referrer;
        emit ReferralSet(msg.sender, referrer);
    }

    /// @notice Sets the referrer for a staker (restricted to owner)
    /// @param staker The address of the staker
    /// @param referrer The address of the referrer
    function setReferrer(address staker, address referrer) external override onlyOwner nonReentrant {
        require(staker != address(0), "Staker cannot be zero address.");
        require(referrer != address(0), "Referrer cannot be zero address.");
        require(staker != referrer, "Staker cannot refer themselves.");
        require(referrers[staker] == address(0), "Referrer already set for staker.");
        require(stakes[referrer].length > 0, "Referrer has no stakes.");

        // Check if the referrer has at least one active stake
        bool hasActiveStake = false;
        uint256 len = stakes[referrer].length;
        for (uint256 i = 0; i < len; i++) {
            if (block.timestamp < stakes[referrer][i].endTimestamp && stakes[referrer][i].stakeValue > 0) {
                hasActiveStake = true;
                break;
            }
        }
        require(hasActiveStake, "Referrer has no active stakes.");

        // Prevent circular referrals
        address currentReferrer = referrer;
        while (currentReferrer != address(0)) {
            if (currentReferrer == staker) {
                revert("Circular referrer relationship detected.");
            }
            currentReferrer = referrers[currentReferrer];
        }

        referrers[staker] = referrer;
        emit ReferralSet(staker, referrer);
    }

    /// @notice Retrieves the number of stakes for a staker
    /// @param staker The address of the staker
    /// @return The number of stakes
    function numStakes(address staker) external view override returns (uint256) {
        return stakes[staker].length;
    }

    /// @notice Checks if a stake is active
    /// @param stakeIndex The index of the stake
    /// @param staker The address of the staker
    /// @return True if the stake is active, false otherwise
    function stakeActive(uint256 stakeIndex, address staker) external view override returns (bool) {
        if (stakeIndex >= stakes[staker].length) {
            return false;
        }
        Stake storage stake = stakes[staker][stakeIndex];
        return stake.stakeValue > 0 && block.timestamp < stake.endTimestamp;
    }

    /// @notice Checks if a contract address is a trusted staking contract
    /// @param contractAddress The address to check
    /// @return True if the contract is trusted, false otherwise
    function isTrustedStakingContract(address contractAddress) external view override returns (bool) {
        // Implement logic to verify if the contract is trusted
        // For example, checking against a list of trusted contracts
        // Here, assuming only the owner can be a trusted contract

        return contractAddress == owner();
    }

    /// @notice Retrieves stake information
    /// @param stakeIndex The index of the stake
    /// @param staker The address of the staker
    /// @return stakeValue The value of the stake
    /// @return stakeDays The duration of the stake in days
    /// @return startTimestamp The start timestamp of the stake
    /// @return endTimestamp The end timestamp of the stake
    function getStakeInfo(uint256 stakeIndex, address staker)
        external
        view
        override
        returns (
            uint256 stakeValue,
            uint256 stakeDays,
            uint256 startTimestamp,
            uint256 endTimestamp
        )
    {
        require(stakeIndex < stakes[staker].length, "Invalid stake index.");
        Stake storage stake = stakes[staker][stakeIndex];
        return (
            stake.stakeValue,
            stake.stakeDays,
            stake.startTimestamp,
            stake.endTimestamp
        );
    }

    /// @notice Sets the maximum stake days
    /// @param _maxStakeDays The new maximum stake days
    function setMaxStakeDays(uint32 _maxStakeDays) external override onlyOwner {
        require(_maxStakeDays <= MAX_STAKE_DAYS, "Exceeds maximum allowed stake days.");
        maxStakeDays = _maxStakeDays;
        emit MaxStakeDaysUpdated(_maxStakeDays);
    }

    /// @notice Activates or deactivates token burning
    /// @param _isTokenBurnActive The new status of token burning
    function setTokenBurnActive(bool _isTokenBurnActive) external override onlyOwner {
        isTokenBurnActive = _isTokenBurnActive;
        emit TokenBurnStatusUpdated(_isTokenBurnActive);
    }

    /// @notice Sets the burn rate percentage
    /// @param _burnRate The new burn rate (0-100)
    function setBurnRate(uint256 _burnRate) external override onlyOwner {
        require(_burnRate <= 100, "Burn rate must be between 0 and 100.");
        burnRate = _burnRate;
        emit BurnRateUpdated(_burnRate);
    }

    /// @notice Activates or deactivates the launch bonus
    /// @param _isLaunchBonusActive The new status of the launch bonus
    function setLaunchBonusActive(bool _isLaunchBonusActive) external override onlyOwner {
        isLaunchBonusActive = _isLaunchBonusActive;
        emit LaunchBonusStatusUpdated(_isLaunchBonusActive);
    }

    /// @notice Sets the launch bonus percentage
    /// @param _launchBonusPercentage The new launch bonus percentage (0-100)
    function setLaunchBonusPercentage(uint256 _launchBonusPercentage) external override onlyOwner {
        require(_launchBonusPercentage <= 100, "Launch bonus must be between 0 and 100.");
        launchBonusPercentage = _launchBonusPercentage;
        emit LaunchBonusPercentageUpdated(_launchBonusPercentage);
    }

    /// @notice Sets the end timestamp for the launch bonus
    /// @param _launchBonusEndTimestamp The new end timestamp
    function setLaunchBonusEndTimestamp(uint256 _launchBonusEndTimestamp) external override onlyOwner {
        require(_launchBonusEndTimestamp > block.timestamp, "End timestamp must be in the future.");
        launchBonusEndTimestamp = _launchBonusEndTimestamp;
        emit LaunchBonusEndTimestampUpdated(_launchBonusEndTimestamp);
    }

    /// @notice Toggles the launch bonus status
    function toggleLaunchBonusStatus() external override onlyOwner {
        isLaunchBonusActive = !isLaunchBonusActive;
        emit LaunchBonusToggled(isLaunchBonusActive);
    }

    /// @notice Adds daily data (to be called by an external mechanism, e.g., a keeper)
    /// @param totalSShares The total stake shares for the day
    /// @param interestPool The interest pool for the day
    function addDailyData(uint256 totalSShares, uint256 interestPool) external onlyOwner {
        uint256 cumulativeInterest = dailyData.length > 0 ? dailyData[dailyData.length - 1].cumulativeInterest : 0;
        cumulativeInterest += interestPool;
        dailyData.push(DailyData({
            totalSShares: totalSShares,
            interestPool: interestPool,
            cumulativeInterest: cumulativeInterest
        }));
        emit DailyDataAdded(totalSShares, interestPool, cumulativeInterest);
    }
}
