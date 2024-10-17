// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

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
