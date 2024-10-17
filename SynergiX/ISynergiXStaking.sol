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

    // Events
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
        _setupRole(STAKING_ROLE, address(_staking));

        // Initialize Variables
        staking = _staking;
        _paused = false;
    }

    /// @notice Authorizes contract upgrades, restricted to ADMIN_ROLE
    /// @param newImplementation The address of the new implementation
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}

    /// @notice Mint function restricted to STAKING_ROLE
    /// @param to The address to mint tokens to
    /// @param amount The amount of tokens to mint
    function mint(address to, uint256 amount) external onlyRole(STAKING_ROLE) {
        _mint(to, amount);
    }

    /// @notice Starts a new stake by delegating to the staking contract
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

        // Delegate the staking process to the staking contract
        uint256 stakeIndex = staking.stakeStart(stakeValue, stakeDays, msg.sender);

        emit StakeStarted(msg.sender, stakeValue, stakeDays, stakeIndex, address(staking));
    }

    /// @notice Ends an active stake by delegating to the staking contract
    /// @param stakeIndex The index of the stake to end
    function stakeEnd(uint256 stakeIndex) external nonReentrant {
        require(hasRole(STAKING_ROLE, address(staking)), "Staking contract lacks STAKING_ROLE");

        // Delegate the stake ending process to the staking contract
        staking.stakeEnd(stakeIndex, msg.sender);

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
