// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol"; 

interface ISynergiXStaking {
    function stakeStart(uint256 stakeValue, uint256 stakeDays, address staker) external returns (uint256);
    function stakeEnd(uint256 stakeIndex, address staker) external;
    function setReferrer(address staker, address referrer) external;
    function MAX_STAKE_DAYS() external view returns (uint256);
    function numStakes(address staker) external view returns (uint256);
    function stakeActive(uint256 stakeIndex, address staker) external view returns (bool);
    function isTrustedStakingContract(address contractAddress) external view returns (bool);
    function getStakeInfo(uint256 stakeIndex, address staker) external view returns (uint256, uint256, uint256, uint256);
} 

contract SynergiXToken is Initializable, ERC20, AccessControl, UUPSUpgradeable {
    using SafeMath for uint256; 

    bytes32 public constant STAKING_ROLE = keccak256("STAKING_ROLE");
    bytes32 public constant TRUSTED_CONTRACT_ROLE = keccak256("TRUSTED_CONTRACT_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE"); 

    ISynergiXStaking public staking;
    bool private _paused; 

    uint256 public constant MAX_STAKING_VALUE = 100000 ether;
    uint256 public constant SECONDS_IN_DAY = 86400;
    uint32 public constant MIN_STAKING_DAYS = 1;
    uint32 public constant MAX_STAKING_DAYS = 365; 

    uint256 public penaltyPool;
    uint256 public rewardPool;
    uint256 private _currentRewardPercentage = 100;
    uint256 private _rewardHalvingBlock = 0;
    uint256 private _lowStakeRewardPercentage = 50;
    uint256 private _mediumStakeRewardPercentage = 75;
    uint256 private _highStakeRewardPercentage = 100;
    uint256 private _lockupPeriod = 30 days;
    uint256 private _lastRewardDistribution; 

    uint256 private constant LOW_STAKE_THRESHOLD = 100 ether;
    uint256 private constant MEDIUM_STAKE_THRESHOLD = 1000 ether;
    uint256 private constant BLOCKS_PER_REWARD_HALVING = 210000; // Halve the reward every 210,000 blocks
contract SynergiXToken is Initializable, ERC20, AccessControl, UUPSUpgradeable {
    using SafeMath for uint256; 

    bytes32 public constant STAKING_ROLE = keccak256("STAKING_ROLE");
    bytes32 public constant TRUSTED_CONTRACT_ROLE = keccak256("TRUSTED_CONTRACT_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE"); 

    ISynergiXStaking public staking;
    bool private _paused; 

    uint256 public constant MAX_STAKING_VALUE = 100000 ether;
    uint256 public constant SECONDS_IN_DAY = 86400;
    uint32 public constant MIN_STAKING_DAYS = 1;
    uint32 public constant MAX_STAKING_DAYS = 365; 

    uint256 public penaltyPool;
    uint256 public rewardPool;
    uint256 private _currentRewardPercentage = 100;
    uint256 private _rewardHalvingBlock = 0;
    uint256 private _lowStakeRewardPercentage = 50;
    uint256 private _mediumStakeRewardPercentage = 75;
    uint256 private _highStakeRewardPercentage = 100;
    uint256 private _lockupPeriod = 30 days;
    uint256 private _lastRewardDistribution; 

    uint256 private constant LOW_STAKE_THRESHOLD = 100 ether;
    uint256 private constant MEDIUM_STAKE_THRESHOLD = 1000 ether;
    uint256 private constant BLOCKS_PER_REWARD_HALVING = 210000; // Halve the reward every 210,000 blocks 

    // Added constants and variables for the new reward calculation
    uint256 private constant REWARD_POOL_FRACTION = 10; // 10% of the total reward pool
    uint256 private constant PENALTY_POOL_FRACTION = 10; // 10% of the total penalty pool
    uint256 private _rewardPoolPercentage = 100; 

    struct Stake {
        uint256 value;
        uint256 startDay;
        uint256 endDay;
        uint256 gracePeriodEnd;
        uint256 reward;
    } 

    mapping(address => Stake[]) private _stakes; 

    event StakeStarted(address indexed staker, uint256 stakeValue, uint256 stakeDays, uint256 indexed stakeIndex, address indexed stakingContract);
    event StakeEnded(address indexed staker, uint256 indexed stakeIndex, uint256 penalty, uint256 reward, address indexed stakingContract); event RewardPoolUpdated(uint256 newRewardPool); event PenaltyPoolUpdated(uint256 newPenaltyPool); 

    function initialize(address admin, ISynergiXStaking _staking) public initializer {
        __ERC20_init("SynergiX Token", "SNX");
        __AccessControl_init(); 

        _setupRole(ADMIN_ROLE, admin);
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(TRUSTED_CONTRACT_ROLE, address(_staking)); 

        staking = _staking;
        _paused = false;
    } 
function calculateReward(uint256 stakeValue) public view returns (uint256) {
    uint256 rewardPercentage; 

    if (stakeValue < LOW_STAKE_THRESHOLD) {
        rewardPercentage = _lowStakeRewardPercentage;
    } else if (stakeValue < MEDIUM_STAKE_THRESHOLD) {
        rewardPercentage = _mediumStakeRewardPercentage;
    } else {
        rewardPercentage = _highStakeRewardPercentage;
    } 

    rewardPercentage = rewardPercentage.mul(_rewardPoolPercentage).div(100); 

    uint256 reward = stakeValue.mul(rewardPercentage).div(100);
    return reward;
} 

// Added logic for utilizing the reward and penalty pools intelligently
function distributeRewardsAndPenalties() external onlyRole(ADMIN_ROLE) {
    uint256 rewardPoolAmount = rewardPool.mul(REWARD_POOL_FRACTION).div(100);
    uint256 penaltyPoolAmount = penaltyPool.mul(PENALTY_POOL_FRACTION).div(100); 

    rewardPool = rewardPool.sub(rewardPoolAmount);
    penaltyPool = penaltyPool.sub(penaltyPoolAmount); 

    emit RewardPoolUpdated(rewardPool);
    emit PenaltyPoolUpdated(penaltyPool); 

    uint256 totalDistribution = rewardPoolAmount.add(penaltyPoolAmount);
    uint256 totalSupply = totalSupply(); 

    // Distribute rewards and penalties proportionally to all token holders
    for (uint256 i = 0; i < getRoleMemberCount(TRUSTED_CONTRACT_ROLE); i++) {
        address trustedContract = getRoleMember(TRUSTED_CONTRACT_ROLE, i); 

        if (staking.isTrustedStakingContract(trustedContract)) {
            for (uint256 j = 0; j < staking.numStakes(trustedContract); j++) {
                if (staking.stakeActive(j, trustedContract)) {
                    (uint256 stakeValue, , , ) = staking.getStakeInfo(j, trustedContract); 

                    uint256 distributionAmount = totalDistribution.mul(stakeValue).div(totalSupply);
                    _mint(trustedContract, distributionAmount);
                }
            }
        }
    } 

    _lastRewardDistribution = block.timestamp;
} 

function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
    super._beforeTokenTransfer(from, to, amount); 

    require(!_paused || hasRole(ADMIN_ROLE, _msgSender()), "Token transfers are paused"); 

    if (from != address(0) && to != address(0) && !hasRole(TRUSTED_CONTRACT_ROLE, from) && !hasRole(TRUSTED_CONTRACT_ROLE, to)) {
        require(block.timestamp >= _lastRewardDistribution + _lockupPeriod, "Token transfers locked");
    }
} 

function pause() external onlyRole(ADMIN_ROLE) {
    _paused = true;
} 

function unpause() external onlyRole(ADMIN_ROLE) {
    _paused = false;
} 

function setRewardPool(uint256 newRewardPool) external onlyRole(ADMIN_ROLE) {
    require(newRewardPool >= rewardPool, "New reward pool must be greater than or equal to the current pool");
    rewardPool = newRewardPool;
    emit RewardPoolUpdated(rewardPool);
} 

function setPenaltyPool(uint256 newPenaltyPool) external onlyRole(ADMIN_ROLE) {
    require(newPenaltyPool >= penaltyPool, "New penalty pool must be greater than or equal to the current pool");
    penaltyPool = newPenaltyPool;
    emit PenaltyPoolUpdated(penaltyPool);
} 

function setRewardPoolPercentage(uint256 rewardPoolPercentage) external onlyRole(ADMIN_ROLE) {
    require(rewardPoolPercentage >= 0 && rewardPoolPercentage <=
contract SynergiXToken is Initializable, ERC20, AccessControl, UUPSUpgradeable {
    using SafeMath for uint256; 

    bytes32 public constant STAKING_ROLE = keccak256("STAKING_ROLE");
    bytes32 public constant TRUSTED_CONTRACT_ROLE = keccak256("TRUSTED_CONTRACT_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE"); 

    ISynergiXStaking public staking;
    bool private _paused; 

    uint256 public constant MAX_STAKING_VALUE = 100000 ether;
    uint256 public constant SECONDS_IN_DAY = 86400;
    uint32 public constant MIN_STAKING_DAYS = 1;
    uint32 public constant MAX_STAKING_DAYS = 365; 

    uint256 public penaltyPool;
    uint256 public rewardPool;
    uint256 private _currentRewardPercentage = 100;
    uint256 private _rewardHalvingBlock = 0;
    uint256 private _lowStakeRewardPercentage = 50;
    uint256 private _mediumStakeRewardPercentage = 75;
    uint256 private _highStakeRewardPercentage = 100;
    uint256 private _lockupPeriod = 30 days;
    uint256 private _lastRewardDistribution; 

    uint256 private constant LOW_STAKE_THRESHOLD = 100 ether;
    uint256 private constant MEDIUM_STAKE_THRESHOLD = 1000 ether;
    uint256 private constant BLOCKS_PER_REWARD_HALVING = 210000; // Halve the reward every 210,000 blocks 

    // Added constants and variables for the new reward calculation
    uint256 private constant REWARD_POOL_FRACTION = 10; // 10% of the total reward pool
    uint256 private constant PENALTY_POOL_FRACTION = 10; // 10% of the total penalty pool
    uint256 private _rewardPoolPercentage = 100; 

    struct Stake {
        uint256 value;
        uint256 startDay;
        uint256 endDay;
        uint256 gracePeriodEnd;
        uint256 reward;
    } 

    mapping(address => Stake[]) private _stakes; 

    event StakeStarted(address indexed staker, uint256 stakeValue, uint256 stakeDays, uint256 indexed stakeIndex, address indexed stakingContract);
    event StakeEnded(address indexed staker, uint256 indexed stakeIndex, uint256 penalty, uint256 reward, address indexed stakingContract); 
    event RewardPoolUpdated(uint256 newRewardPool); 
    event PenaltyPoolUpdated(uint256 newPenaltyPool); 

    function initialize(address admin, ISynergiXStaking _staking) public initializer {
        __ERC20_init("SynergiX Token", "SNX");
        __AccessControl_init(); 

        _setupRole(ADMIN_ROLE, admin);
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(TRUSTED_CONTRACT_ROLE, address(_staking)); 

        staking = _staking;
        _paused = false;
    } 

    function _authorizeUpgrade(address) internal override onlyRole(ADMIN_ROLE) {} 

    function stake(uint256 stakeValue, uint256 stakeDays) external {
        require(stakeValue <= MAX_STAKING_VALUE, "Stake value exceeds maximum limit");
        require(stakeDays >= MIN_STAKING_DAYS && stakeDays <= MAX_STAKING_DAYS, "Invalid staking duration"); 

        uint256 stakeIndex = staking.stakeStart(stakeValue, stakeDays, _msgSender());
        _stakes[_msgSender()].push(Stake(stakeValue, block.timestamp 

function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
    super._beforeTokenTransfer(from, to, amount); 

    require(!_paused || hasRole(ADMIN_ROLE, _msgSender()), "Token transfers are paused"); 

    if (from != address(0) && to != address(0) && !hasRole(TRUSTED_CONTRACT_ROLE, from) && !hasRole(TRUSTED_CONTRACT_ROLE, to)) {
        require(block.timestamp >= _lastRewardDistribution + _lockupPeriod, "Token transfers locked");
    }
} 

function pause() external onlyRole(ADMIN_ROLE) {
    _paused = true;
} 

function unpause() external onlyRole(ADMIN_ROLE) {
    _paused = false;
} 

function setRewardPool(uint256 newRewardPool) external onlyRole(ADMIN_ROLE) {
    require(newRewardPool >= rewardPool, "New reward pool must be greater than or equal to the current pool");
    rewardPool = newRewardPool;
    emit RewardPoolUpdated(rewardPool);
} 

function setPenaltyPool(uint256 newPenaltyPool) external onlyRole(ADMIN_ROLE) {
    require(newPenaltyPool >= penaltyPool, "New penalty pool must be greater than or equal to the current pool");
    penaltyPool = newPenaltyPool;
    emit PenaltyPoolUpdated(penaltyPool);
} 

function setRewardPoolPercentage(uint256 rewardPoolPercentage) external onlyRole(ADMIN_ROLE) {
    require(rewardPoolPercentage >= 0 && rewardPoolPercentage <= 100, "Invalid reward pool percentage");
    _rewardPoolPercentage = rewardPoolPercentage;
}
}
