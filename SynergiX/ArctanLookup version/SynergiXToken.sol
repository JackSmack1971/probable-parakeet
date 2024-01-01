// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";  
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";

contract Synergix is ERC20, ReentrancyGuard, Ownable, Pausable {

    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bool private _notEntered;

    uint256 public constant TOTAL_SUPPLY = 100_000_000 * 10**18;

    uint256 public burnRate;
    
    IUniswapV2Router02 private uniswapV2Router;

    event BurnRateUpdated(uint256 burnRate);

    modifier nonReentrant() {
        require(!_notEntered, "Reentrant call");
        _notEntered = true;
        _;
        _notEntered = false;
    }

    constructor(address _uniswapV2Router) ERC20("Synergix", "SYN") {
        uniswapV2Router = IUniswapV2Router02(_uniswapV2Router);
        _mint(msg.sender, TOTAL_SUPPLY);
    }

    function setBurnRate(uint256 newBurnRate) external onlyOwner whenNotPaused nonReentrant {
        burnRate = newBurnRate;
        emit BurnRateUpdated(newBurnRate);
    }

    function pause() public onlyOwner whenNotPaused {
        _pause();
    }

    function unpause() public onlyOwner whenPaused {
        _unpause();
    }

    function recoverStuckTokens(address token) external onlyOwner nonReentrant {
        uint256 amount = IERC20(token).balanceOf(address(this));
        IERC20(token).safeTransfer(owner(), amount);
    }

    function _swapAndLiquify() internal {
        // Swap and liquify logic
        uint256 tokens = balanceOf(address(this));
        uint256 half = tokens.div(2);
        uint256 initialEth = address(this).balance;

        // Swap tokens for ETH
        swapTokensForEth(half); 

        // Amount of ETH after swap
        uint256 newEth = address(this).balance.sub(initialEth);

        // Add liquidity
        addLiquidity(half, newEth);
    }

    // Internal swap/liquidity functions
    function swapTokensForEth(uint256 tokenAmount) private {
        address[] memory path = new address[](2);
        path[0] = address(this);
        path[1] = uniswapV2Router.WETH();

        uniswapV2Router.swapExactTokensForETHSupportingFeeOnTransferTokens(
            tokenAmount,
            0, // Accept any amount of ETH
            path,
            address(this),
            block.timestamp
        );
    }
    
    function addLiquidity(uint256 tokenAmount, uint256 ethAmount) private {
        // Approve tokens
        _approve(address(this), address(uniswapV2Router), tokenAmount);

        // Add liquidity
        uniswapV2Router.addLiquidityETH{value: ethAmount}(
            address(this),
            tokenAmount,
            0, // slippage is unavoidable
            0, // slippage is unavoidable
            owner(),
            block.timestamp
        );
    }

}
