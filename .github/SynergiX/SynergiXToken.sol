// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol"; 

interface ISynergiXStaking {
    function stakeStart(uint256 stakeValue, uint32 stakeDays, address staker) external;
    function stakeEnd(uint256 stakeIndex, address staker) external;
    function setReferrer(address staker, address referrer) external;
    function MAX_STAKE_DAYS() external view returns (uint256);
} 

contract SynergiXToken is ERC20, Ownable {
    // Constants
    uint256 public constant INITIAL_SUPPLY = 1000000000 * 10**18; // Initial supply of 1 billion SYN 

    // Staking contract
    ISynergiXStaking public staking; 

    // Events
    event StakeStarted(address indexed staker, uint256 stakeValue, uint32 stakeDays);
    event StakeEnded(address indexed staker, uint256 stakeIndex);
    event ReferrerSet(address indexed staker, address indexed referrer); 

    constructor(ISynergiXStaking _staking) ERC20("SynergiX Token", "SYN") {
        staking = _staking;
        _mint(msg.sender, INITIAL_SUPPLY);
    } 

    // Allows users to start staking their SYN tokens
    function stakeStart(uint256 stakeValue, uint32 stakeDays) external {
        require(stakeValue > 0, "Staking value must be greater than 0");
        require(stakeDays > 0, "Staking days must be greater than 0");
        // Add check for maximum staking days allowed
        require(stakeDays <= staking.MAX_STAKE_DAYS(), "Staking days exceed the maximum allowed"); 

        _approve(msg.sender, address(staking), stakeValue);
        staking.stakeStart(stakeValue, stakeDays, msg.sender);
        emit StakeStarted(msg.sender, stakeValue, stakeDays);
    } 

    // Allows users to end their staking position
    function stakeEnd(uint256 stakeIndex) external {
        staking.stakeEnd(stakeIndex, msg.sender);
        emit StakeEnded(msg.sender, stakeIndex);
    } 

    // Allows users to set their referrer in the staking contract
    function setReferrer(address referrer) external {
        require(msg.sender != referrer, "You cannot refer yourself");
        staking.setReferrer(msg.sender, referrer);
        emit ReferrerSet(msg.sender, referrer);
    } 

    // Allows the owner to update the staking contract address
    function setStakingContract(ISynergiXStaking _staking) external onlyOwner {
        require(address(_staking) != address(0), "Invalid staking contract address");
        staking = _staking;
    }
}
