// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "./ISynergiXStaking.sol"; 

contract SynergiXStaking is ISynergiXStaking, Ownable {
    using SafeMath for uint256; 

    // Constants
    uint256 public constant MAX_STAKE_DAYS = 5555;
    uint256 public constant BONUS_MAX = 200; // Percentage
    uint256 public constant BONUS_MIN_STAKE = 150 * 10**6; // 150 million SYN
    uint256 public constant MIN_STAKE_VALUE = 1 * 10**6; // 1 million SYN 

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
    ERC20 public token;
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

    constructor(ERC20 _token) {
        token = _token;
        shareRate = 1 * 10**18;
        isLaunchBonusActive = true;
        launchBonusEndTimestamp = block.timestamp + 30 days;
    } 

    // Main staking functions
    function stakeStart(uint256 stakeValue, uint32 stakeDays, address staker) external override {
        require(stakeValue >= MIN_STAKE_VALUE, "Stake value must be at least 1 million SYN.");
        require(stakeDays > 0 && stakeDays <= maxStakeDays, "Invalid stake days."); 

        token.transferFrom(staker, address(this), stakeValue); 

        uint256 sShares = calcStakeShares(stakeValue, stakeDays);
        uint256 startTimestamp = block.timestamp;
        uint256 endTimestamp = startTimestamp + stakeDays * 86400; 

        stakes[staker].push(Stake(stakeValue, stakeDays, startTimestamp, endTimestamp, sShares)); 

        // Emit StakeStarted event
        emit StakeStarted(staker, stakeValue, stakeDays, sShares); 

             // Reward referrals if applicable
        _rewardReferral(staker, stakeValue);
    } 

    function calcStakeShares(uint256 stakeValue, uint32 stakeDays) public view returns (uint256) {
        uint256 bonusMultiplier = (BONUS_MAX * (stakeDays - 1)) / (maxStakeDays - 1);
        uint256 bonus = 0; 

        if (stakeValue >= BONUS_MIN_STAKE) {
            bonus = stakeValue.mul(bonusMultiplier).div(100);
        } 

        uint256 effectiveValue = stakeValue.add(bonus);
        return effectiveValue.mul(10**18).div(shareRate);
    } 

    function _rewardReferral(address staker, uint256 stakeValue) private {
        address referrer = referrers[staker];
        if (referrer != address(0)) {
            uint256 referrerReward = stakeValue.mul(REFERRER_REWARD).div(100);
            uint256 referredReward = stakeValue.mul(REFERRED_REWARD).div(100);
            token.transfer(referrer, referrerReward);
            token.transfer(staker, referredReward); 

            // Emit ReferralRewarded event
            emit ReferralRewarded(referrer, staker, referrerReward, referredReward);
        }
    } 

    function stakeEnd(uint256 stakeIndex, address staker) external override {
        require(stakeIndex < stakes[staker].length, "Invalid stake index.");
        Stake storage stake = stakes[staker][stakeIndex];
        require(stake.endTimestamp <= block.timestamp, "Stake has not ended yet.");
        require(stake.stakeValue > 0, "Stake has already been ended."); 

        // Calculate payout
        uint256 payout = _calculatePayout(staker, stakeIndex); 

        // Remove the stake from the staker's stakes
        stake.stakeValue = 0;
        stake.sShares = 0; 

        // Burn tokens if the feature is active
        if (isTokenBurnActive) {
            uint256 burnAmount = payout.mul(burnRate).div(100);
            payout = payout.sub(burnAmount);
            token.burn(burnAmount);
        } 

        token.transfer(staker, payout); 

        // Emit StakeEnded event
        emit StakeEnded(staker, stakeIndex, payout);
    } 

    function _calculatePayout(address staker, uint256 stakeIndex) internal view returns (uint256) {
        uint256 startDayIndex = stakes[staker][stakeIndex].startTimestamp / 86400;
        uint256 endDayIndex = stakes[staker][stakeIndex].endTimestamp / 86400;
        uint256 sShares = stakes[staker][stakeIndex].sShares; 

        uint256 totalCumulativeInterest = dailyData[endDayIndex].cumulativeInterest.sub(dailyData[startDayIndex].cumulativeInterest);
        uint256 interest = totalCumulativeInterest.mul(sShares).div(dailyData[endDayIndex].totalSShares); 

        return stakes[staker][stakeIndex].stakeValue.add(interest);
    } 

    // Getters and setters for the contract features 

    function setMaxStakeDays(uint32 _maxStakeDays) external onlyOwner {
        require(_maxStakeDays <= MAX_STAKE_DAYS, "Exceeds maximum allowed stake days.");
        maxStakeDays = _maxStakeDays;
    } 

        function setTokenBurnActive(bool _isTokenBurnActive) external onlyOwner {
        isTokenBurnActive = _isTokenBurnActive;
    } 

    function setBurnRate(uint256 _burnRate) external onlyOwner {
        require(_burnRate <= 100, "Burn rate must be between 0 and 100.");
        burnRate = _burnRate;
    } 

    function setLaunchBonusActive(bool _isLaunchBonusActive) external onlyOwner {
        isLaunchBonusActive = _isLaunchBonusActive;
    } 

    function setLaunchBonusPercentage(uint256 _launchBonusPercentage) external onlyOwner {
        require(_launchBonusPercentage <= 100, "Launch bonus must be between 0 and 100.");
        launchBonusPercentage = _launchBonusPercentage;
    } 

    function setLaunchBonusEndTimestamp(uint256 _launchBonusEndTimestamp) external onlyOwner {
        require(_launchBonusEndTimestamp > block.timestamp, "End timestamp must be in the future.");
        launchBonusEndTimestamp = _launchBonusEndTimestamp;
    } 

    function toggleLaunchBonusStatus() external onlyOwner {
        isLaunchBonusActive = !isLaunchBonusActive;
    }
}
