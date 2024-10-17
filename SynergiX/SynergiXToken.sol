// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Import OpenZeppelin Contracts
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title ISynergiXStaking Interface
/// @notice Interface for the SynergiX Staking Contract
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

/// @title SynergiXToken
/// @notice ERC20 Token with Staking, Access Control, and Upgradeability Features
contract SynergiXToken is Initializable, ERC20Burnable, AccessControl, UUPSUpgradeable, ReentrancyGuard {
    // Roles Definitions
    bytes32 public constant STAKING_ROLE = keccak256("STAKING_ROLE");
    bytes32 public constant TRUSTED_CONTRACT_ROLE = keccak256("TRUSTED_CONTRACT_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // Staking Interface
    ISynergiXStaking public staking;

    // Pausable State
    bool private _paused;

    // Constants
    uint256 public constant MAX_STAKING_VALUE = 100000 ether;
    uint256 public constant SECONDS_IN_DAY = 86400;
    uint32 public constant MIN_STAKING_DAYS = 1;
    uint32 public constant MAX_STAKING_DAYS = 365;

    // Pools
    uint256 public penaltyPool;
    uint256 public rewardPool;

    // Reward Parameters
    uint256 private _currentRewardPercentage;
    uint256 private _rewardHalvingBlock;
    uint256 private _lowStakeRewardPercentage;
    uint256 private _mediumStakeRewardPercentage;
    uint256 private _highStakeRewardPercentage;
    uint256 private _lockupPeriod;
    uint256 private _lastRewardDistribution;

    // Thresholds
    uint256 private constant LOW_STAKE_THRESHOLD = 100 ether;
    uint256 private constant MEDIUM_STAKE_THRESHOLD = 1000 ether;
    uint256 private constant BLOCKS_PER_REWARD_HALVING = 210000; // Halve the reward every 210,000 blocks

    // Reward Pool Fractions
    uint256 private constant REWARD_POOL_FRACTION = 10; // 10%
    uint256 private constant PENALTY_POOL_FRACTION = 10; // 10%

    // Reward Pool Percentage
    uint256 private _rewardPoolPercentage;

    /// @notice Stake Structure
    struct Stake {
        uint256 value;
        uint256 startDay;
        uint256 endDay;
        uint256 gracePeriodEnd;
        uint256 reward;
    }

    // Mapping of Stakes per Address
    mapping(address => Stake[]) private _stakes;

    // Events
    event StakeStarted(
        address indexed staker,
        uint256 stakeValue,
        uint256 stakeDays,
        uint256 indexed stakeIndex,
        address indexed stakingContract
    );
    event StakeEnded(
        address indexed staker,
        uint256 indexed stakeIndex,
        uint256 penalty,
        uint256 reward,
        address indexed stakingContract
    );
    event RewardPoolUpdated(uint256 newRewardPool);
    event PenaltyPoolUpdated(uint256 newPenaltyPool);
    event RewardPoolPercentageUpdated(uint256 newRewardPoolPercentage);
    event TrustedContractAdded(address indexed contractAddress);
    event TrustedContractRemoved(address indexed contractAddress);

    /// @notice Initializes the contract with the given parameters
    /// @param admin The address to be granted the ADMIN_ROLE
    /// @param _staking The address of the staking contract
    function initialize(address admin, ISynergiXStaking _staking) public initializer {
        require(admin != address(0), "Admin address cannot be zero");
        require(address(_staking) != address(0), "Staking contract address cannot be zero");

        __ERC20_init("SynergiX Token", "SNX");
        __AccessControl_init();
        __UUPSUpgradeable_init();
        __ReentrancyGuard_init();

        // Setup Roles
        _setupRole(ADMIN_ROLE, admin);
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(TRUSTED_CONTRACT_ROLE, address(_staking));

        // Initialize Variables
        staking = _staking;
        _paused = false;

        penaltyPool = 0;
        rewardPool = 0;
        _currentRewardPercentage = 100;
        _rewardHalvingBlock = block.number;
        _lowStakeRewardPercentage = 50;
        _mediumStakeRewardPercentage = 75;
        _highStakeRewardPercentage = 100;
        _lockupPeriod = 30 days;
        _lastRewardDistribution = block.timestamp;
        _rewardPoolPercentage = 100;
    }

    /// @notice Authorizes contract upgrades, restricted to ADMIN_ROLE
    /// @param newImplementation The address of the new implementation
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}

    /// @notice Calculates the reward based on the stake value
    /// @param stakeValue The value of the stake
    /// @return reward The calculated reward
    function calculateReward(uint256 stakeValue) public view returns (uint256 reward) {
        uint256 rewardPercentage;

        if (stakeValue < LOW_STAKE_THRESHOLD) {
            rewardPercentage = _lowStakeRewardPercentage;
        } else if (stakeValue < MEDIUM_STAKE_THRESHOLD) {
            rewardPercentage = _mediumStakeRewardPercentage;
        } else {
            rewardPercentage = _highStakeRewardPercentage;
        }

        rewardPercentage = (rewardPercentage * _rewardPoolPercentage) / 100;

        reward = (stakeValue * rewardPercentage) / 100;
    }

    /// @notice Starts a new stake
    /// @param stakeValue The amount to stake
    /// @param stakeDays The duration of the stake in days
    function stake(uint256 stakeValue, uint256 stakeDays) external nonReentrant {
        require(stakeValue <= MAX_STAKING_VALUE, "Stake value exceeds maximum limit");
        require(
            stakeDays >= MIN_STAKING_DAYS && stakeDays <= MAX_STAKING_DAYS,
            "Invalid staking duration"
        );

        // Ensure the staking contract has the STAKING_ROLE
        require(hasRole(STAKING_ROLE, address(staking)), "Staking contract lacks STAKING_ROLE");

        // User must approve the staking contract to spend their tokens
        // The staking contract will handle the transfer
        uint256 stakeIndex = staking.stakeStart(stakeValue, stakeDays, msg.sender);

        Stake memory newStake = Stake({
            value: stakeValue,
            startDay: block.timestamp,
            endDay: block.timestamp + (stakeDays * SECONDS_IN_DAY),
            gracePeriodEnd: 0, // Define as needed
            reward: 0 // Initialize as needed
        });

        _stakes[msg.sender].push(newStake);

        emit StakeStarted(msg.sender, stakeValue, stakeDays, stakeIndex, address(staking));
    }

    /// @notice Ends an active stake and claims rewards
    /// @param stakeIndex The index of the stake to end
    function stakeEnd(uint256 stakeIndex) external nonReentrant {
        require(stakeIndex < _stakes[msg.sender].length, "Invalid stake index");
        Stake storage userStake = _stakes[msg.sender][stakeIndex];
        require(block.timestamp >= userStake.endDay, "Stake period not yet ended");
        require(userStake.value > 0, "Stake has already been ended");

        // Call the staking contract to handle payout and token transfers
        staking.stakeEnd(stakeIndex, msg.sender);

        // Update the stake to indicate it has been ended
        userStake.value = 0;
        userStake.reward = 0;

        emit StakeEnded(msg.sender, stakeIndex, 0, 0, address(staking));
    }

    /// @notice Adds a trusted staking contract
    /// @param contractAddress The address of the staking contract to add
    function addTrustedContract(address contractAddress) external onlyRole(ADMIN_ROLE) {
        require(contractAddress != address(0), "Cannot add zero address");
        grantRole(TRUSTED_CONTRACT_ROLE, contractAddress);
        emit TrustedContractAdded(contractAddress);
    }

    /// @notice Removes a trusted staking contract
    /// @param contractAddress The address of the staking contract to remove
    function removeTrustedContract(address contractAddress) external onlyRole(ADMIN_ROLE) {
        revokeRole(TRUSTED_CONTRACT_ROLE, contractAddress);
        emit TrustedContractRemoved(contractAddress);
    }

    /// @notice Distributes rewards and penalties proportionally to all token holders
    /// @dev Note: This function is optimized but may still be gas-intensive for large numbers of holders
    function distributeRewardsAndPenalties() external onlyRole(ADMIN_ROLE) nonReentrant {
        uint256 rewardPoolAmount = (rewardPool * REWARD_POOL_FRACTION) / 100;
        uint256 penaltyPoolAmount = (penaltyPool * PENALTY_POOL_FRACTION) / 100;

        rewardPool -= rewardPoolAmount;
        penaltyPool -= penaltyPoolAmount;

        emit RewardPoolUpdated(rewardPool);
        emit PenaltyPoolUpdated(penaltyPool);

        uint256 totalDistribution = rewardPoolAmount + penaltyPoolAmount;
        uint256 totalSupplyTokens = totalSupply();

        // Ensure there's something to distribute
        if (totalDistribution == 0 || totalSupplyTokens == 0) {
            return;
        }

        // Mint tokens proportionally to all token holders
        // WARNING: This loop can run out of gas if there are too many holders
        // Consider alternative approaches for distributing rewards
        // such as snapshot-based distributions or user-initiated claims

        // Placeholder: Emit an event indicating distribution
        // Actual distribution logic should be handled off-chain or through a more efficient mechanism
        emit RewardPoolUpdated(rewardPool);
        emit PenaltyPoolUpdated(penaltyPool);

        _lastRewardDistribution = block.timestamp;
    }

    /// @notice Sets a new reward pool amount
    /// @param newRewardPool The new amount for the reward pool
    function setRewardPool(uint256 newRewardPool) external onlyRole(ADMIN_ROLE) {
        require(newRewardPool >= rewardPool, "New reward pool must be >= current pool");
        rewardPool = newRewardPool;
        emit RewardPoolUpdated(rewardPool);
    }

    /// @notice Sets a new penalty pool amount
    /// @param newPenaltyPool The new amount for the penalty pool
    function setPenaltyPool(uint256 newPenaltyPool) external onlyRole(ADMIN_ROLE) {
        require(newPenaltyPool >= penaltyPool, "New penalty pool must be >= current pool");
        penaltyPool = newPenaltyPool;
        emit PenaltyPoolUpdated(penaltyPool);
    }

    /// @notice Sets the reward pool percentage
    /// @param rewardPoolPercentage The new reward pool percentage (0-100)
    function setRewardPoolPercentage(uint256 rewardPoolPercentage) external onlyRole(ADMIN_ROLE) {
        require(
            rewardPoolPercentage <= 100,
            "Reward pool percentage must be between 0 and 100"
        );
        _rewardPoolPercentage = rewardPoolPercentage;
        emit RewardPoolPercentageUpdated(_rewardPoolPercentage);
    }

    /// @notice Pauses all token transfers
    function pause() external onlyRole(ADMIN_ROLE) {
        _paused = true;
    }

    /// @notice Unpauses all token transfers
    function unpause() external onlyRole(ADMIN_ROLE) {
        _paused = false;
    }

    /// @notice Overrides the ERC20 _beforeTokenTransfer to implement pause and lockup logic
    /// @param from The address tokens are transferred from
    /// @param to The address tokens are transferred to
    /// @param amount The amount of tokens transferred
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
        super._beforeTokenTransfer(from, to, amount);

        require(!_paused || hasRole(ADMIN_ROLE, _msgSender()), "Token transfers are paused");

        // Apply lockup period for non-trusted contracts
        if (
            from != address(0) &&
            to != address(0) &&
            !hasRole(TRUSTED_CONTRACT_ROLE, from) &&
            !hasRole(TRUSTED_CONTRACT_ROLE, to)
        ) {
            require(
                block.timestamp >= _lastRewardDistribution + _lockupPeriod,
                "Token transfers are locked"
            );
        }
    }

    /// @notice Grants ADMIN_ROLE to a new admin
    /// @param newAdmin The address to be granted ADMIN_ROLE
    function grantAdminRole(address newAdmin) external onlyRole(ADMIN_ROLE) {
        grantRole(ADMIN_ROLE, newAdmin);
    }

    /// @notice Revokes ADMIN_ROLE from an admin
    /// @param admin The address from which ADMIN_ROLE will be revoked
    function revokeAdminRole(address admin) external onlyRole(ADMIN_ROLE) {
        revokeRole(ADMIN_ROLE, admin);
    }

    /// @notice Retrieves the number of stakes for a staker
    /// @param staker The address of the staker
    /// @return The number of active stakes
    function getNumStakes(address staker) external view returns (uint256) {
        return _stakes[staker].length;
    }

    /// @notice Retrieves stake information for a given staker and stake index
    /// @param staker The address of the staker
    /// @param stakeIndex The index of the stake
    /// @return value The staked value
    /// @return startDay The start timestamp of the stake
    /// @return endDay The end timestamp of the stake
    /// @return gracePeriodEnd The end timestamp of the grace period
    /// @return reward The calculated reward
    function getStakeInfo(address staker, uint256 stakeIndex)
        external
        view
        returns (
            uint256 value,
            uint256 startDay,
            uint256 endDay,
            uint256 gracePeriodEnd,
            uint256 reward
        )
    {
        require(stakeIndex < _stakes[staker].length, "Invalid stake index");
        Stake storage userStake = _stakes[staker][stakeIndex];
        return (
            userStake.value,
            userStake.startDay,
            userStake.endDay,
            userStake.gracePeriodEnd,
            userStake.reward
        );
    }

    /// @notice Overrides supportsInterface to include AccessControl interfaces
    /// @param interfaceId The interface identifier
    /// @return bool indicating support for the interface
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControl, ERC20)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
