// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol"; 

interface IArctanLookup {
    function arctan(uint256 x) external pure returns (uint256);
} 

contract Synergix is ERC20, Ownable {
    using SafeMath for uint256; 

    uint256 private constant TOTAL_SUPPLY = 100_000_000 * 10**18;
    uint256 private constant INITIAL_PRICE = 100 * 10**18;
    uint256 private constant MINT_PER_DAY = 10_000 * 10**18;
    uint256 private constant BURN_RATE_LIMIT = 10;
    uint256 private constant ARCTAN_LOOKUP_MULTIPLIER = 100;
    uint256 private constant MINIMUM_LIQUIDITY = 10**3;
    uint256 private constant FEE_PERCENTAGE = 1; 

    uint256 private _burnRate;
    uint256[] private _arctanLookupTable; 

    address private _arctanLookupContract;
    IUniswapV2Router02 private _uniswapV2Router;
    address private _uniswapV2Pair;
    bool private _inSwapAndLiquify; 

    event BurnRateUpdated(uint256 burnRate);
    event LiquidityAdded(uint256 tokenAmount, uint256 etherAmount);
    event SwapAndLiquify(uint256 tokensSwapped, uint256 ethReceived, uint256 tokensIntoLiquidity); 

    constructor(address arctanLookupContract, address uniswapV2Router) ERC20("Synergix", "SYN") {
        require(arctanLookupContract != address(0), "Invalid arctanLookupContract");
        require(uniswapV2Router != address(0), "Invalid UniswapV2Router");
        _arctanLookupContract = arctanLookupContract;
        _uniswapV2Router = IUniswapV2Router02(uniswapV2Router);
        _burnRate = 0;
        _mint(msg.sender, TOTAL_SUPPLY); 

        // Initialize lookup table for inverse tangent function
        _arctanLookupTable = new uint256[](101);
        for (uint256 i = 0; i < 101; i++) {
            _arctanLookupTable[i] = IArctanLookup(_arctanLookupContract).arctan(i);
        } 

        // Create a Uniswap V2 pair for this new token
        _uniswapV2Pair = IUniswapV2Factory(_uniswapV2Router.factory()).createPair(address(this), _uniswapV2Router.WETH()); 

        // Exclude owner and this contract from fee
        _uniswapV2Router.excludeSender(address(this));
        _uniswapV2Router.excludeRecipient(address(this));
        _uniswapV2Router.excludeSender(owner());
        _uniswapV2Router.excludeRecipient(owner()); 

       // Approve the maximum amount for the Uniswap V2 router _approve(address(this), address(_uniswapV2Router), type(uint256).max); 
}
function buy() external payable {
    require(msg.value > 0, "Must send ether");
    uint256 tokens = calculateTokens(msg.value);
    _mint(msg.sender, tokens);
} 

function sell(uint256 amount) external {
    require(amount > 0, "Amount must be greater than zero");
    uint256 etherAmount = calculateEtherAmount(amount);
    require(address(this).balance >= etherAmount, "Insufficient ether balance");
    _burn(msg.sender, amount);
    payable(msg.sender).transfer(etherAmount);
} 

function calculateTokens(uint256 etherAmount) public view returns (uint256) {
    require(etherAmount > 0, "Ether amount must be greater than zero");
    uint256 tokens = etherAmount.mul(INITIAL_PRICE);
    uint256 curveTokens = calculateCurveTokens(tokens);
    uint256 fee = curveTokens.mul(FEE_PERCENTAGE).div(100);
    return curveTokens.sub(fee);
} 

function calculateEtherAmount(uint256 tokenAmount) public view returns (uint256) {
    require(tokenAmount > 0, "Token amount must be greater than zero");
    uint256 fee = tokenAmount.mul(FEE_PERCENTAGE).div(100);
    uint256 curveTokens = tokenAmount.add(fee);
    uint256 etherAmount = calculateCurveTokens(curveTokens).div(INITIAL_PRICE);
    return etherAmount;
} 

function calculateCurveTokens(uint256 tokens) public view returns (uint256) {
    uint256 daysSinceLaunch = block.timestamp.div(1 days);
    uint256 mintableTokens = daysSinceLaunch.mul(MINT_PER_DAY);
    if (mintableTokens > TOTAL_SUPPLY) {
        mintableTokens = TOTAL_SUPPLY;
    }
    uint256 maxBurnRate = calculateMaxBurnRate();
    uint256 burnRate = maxBurnRate.mul(tokens).div(TOTAL_SUPPLY);
    if (burnRate > BURN_RATE_LIMIT) {
        burnRate = BURN_RATE_LIMIT;
    }
    uint256 curveTokens = tokens.mul(10000 - burnRate).div(10000);
    if (mintableTokens > 0 && TOTAL_SUPPLY.sub(totalSupply()) >= mintableTokens) {
        curveTokens = curveTokens.add(mintableTokens.div(365));
    }
    return curveTokens;
} 

function calculateMaxBurnRate() public view returns (uint256) {
    uint256 daysSinceLaunch = block.timestamp.div(1 days);
    uint256 maxBurnRate = daysSinceLaunch.mul(ARCTAN_LOOKUP_MULTIPLIER).div(365);
    if (maxBurnRate > 100) {
        maxBurnRate = 100;
    }
    return maxBurnRate;
} 

function setBurnRate(uint256 burnRate) external onlyOwner {
    require(burnRate <= BURN_RATE_LIMIT, "Burn rate exceeds limit");
    _burnRate = burnRate;
    emit BurnRateUpdated(burnRate);
} 

function getBurnRate() public view returns (uint256) {
    return _burnRate;
} 

function _createUniswapPair(address token) private returns (address) {
    address pair = _uniswapFactory.getPair(token, _uniswapRouterContract.WETH());
    if (pair == address(0)) {
        pair = _uniswapFactory.createPair(token, _uniswapRouterContract.WETH());
    }
    return pair;
}
    uint256 halfTokens = tokens.div(2);
function _swapAndLiquify(uint256 tokens) private { uint256 initialBalance = address(this).balance; _swapTokensForEth(halfTokens); uint256 newBalance = address(this).balance.sub(initialBalance); _addLiquidity(halfTokens, newBalance); emit SwapAndLiquify(halfTokens, newBalance, tokens.sub(halfTokens)); 
}
function _swapTokensForEth(uint256 tokenAmount) private {
    address[] memory path = new address[](2);
    path[0] = address(this);
    path[1] = _uniswapRouterContract.WETH();
    _approve(address(this), address(_uniswapRouterContract), tokenAmount);
    _uniswapRouterContract.swapExactTokensForETHSupportingFeeOnTransferTokens(
        tokenAmount,
        0,
        path,
        address(this),
        block.timestamp
    );
} 

function _addLiquidity(uint256 tokenAmount, uint256 ethAmount) private {
    _approve(address(this), address(_uniswapRouterContract), tokenAmount);
    _uniswapRouterContract.addLiquidityETH{value: ethAmount}(
        address(this),
        tokenAmount,
        0,
        0,
        address(this),
        block.timestamp
    );
    uint256 liquidity = balanceOf(address(this));
    if (liquidity > MINIMUM_LIQUIDITY) {
        _transfer(address(this), _uniswapV2Pair, liquidity);
    }
} 

receive() external payable {}
}
