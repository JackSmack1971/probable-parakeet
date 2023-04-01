// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol"; 
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; 

import "./IUniswapV2Router02.sol";
import "./IUniswapV2Factory.sol";
import "./IUniswapV2Pair.sol"; 

contract MyToken is ERC20, ReentrancyGuard {
    using SafeMath for uint256;
    using SafeERC20 for IERC20; 

    IUniswapV2Router02 public uniswapV2Router;
    address public uniswapV2Pair; 

    uint256 private constant _REFLECTION_TOTAL = (~uint256(0) - (~uint256(0) % 10**9));
    uint256 private _totalSupply;
    uint256 private _liquidityFee;
    uint256 private _minLiquidityFee;
    uint256 private _maxLiquidityFee;
    uint256 private _targetLiquidity;
    uint256 private _targetLiquidityDenominator;
    uint256 private _rebaseThreshold;
    uint256 private _minBuybackBalance;
    uint256 private _dividendPercentage;
    uint256 private _lastDividendRelease;
    uint256 private _dividendReleaseInterval;
    address private _deadAddress = 0x000000000000000000000000000000000000dEaD; 

    constructor() ERC20("MyToken", "MTK") {
        _totalSupply = 10**9 * 10**18;
        _liquidityFee = 5;
        _minLiquidityFee = 1;
        _maxLiquidityFee = 10;
        _targetLiquidity = 25;
        _targetLiquidityDenominator = 100;
        _rebaseThreshold = 10**18;
        _minBuybackBalance = 1 ether;
        _dividendPercentage = 10;
        _lastDividendRelease = block.timestamp;
        _dividendReleaseInterval = 1 days; 

        // Create a Uniswap pair for this token
        uniswapV2Router = IUniswapV2Router02(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
        address factory = uniswapV2Router.factory();
        uniswapV2Pair = IUniswapV2Factory(factory).getPair(address(this), uniswapV2Router.WETH());
        if (uniswapV2Pair == address(0)) {
            uniswapV2Pair = IUniswapV2Factory(factory).createPair(address(this), uniswapV2Router.WETH());
        } 

        _reflections[msg.sender] = _REFLECTION_TOTAL; 

        emit Transfer(address(0), msg.sender, _totalSupply);
    } 

    function _getValues(uint256 tAmount) private view returns (uint256, uint256) {
        uint256 tFee = tAmount.mul(_liquidityFee).div(100);
        uint256 tTransferAmount = tAmount.sub(tFee);
        return (tTransferAmount, tFee);
    } 

    function reflectionFromToken(uint256 tAmount, bool deductTransferFee) public view returns(uint256) {
        require(tAmount <= _total 

    } 

    function tokenFromReflection(uint256 rAmount) public view returns(uint256) {
        require(rAmount <= _REFLECTION_TOTAL, "Amount must be less than reflection total");
        uint256 currentRate = _getRate();
        return rAmount.div(currentRate);
    } 

    function _getRate() private view returns (uint256) {
        (uint256 reflectionSupply, uint256 tokenSupply) = _getCurrentSupply();
        return reflectionSupply.div(tokenSupply);
    } 

    function _getCurrentSupply() private view returns (uint256, uint256) {
        uint256 rSupply = _REFLECTION_TOTAL;
        uint256 tSupply = _totalSupply;
        for (uint256 i = 0; i < _excluded.length; i++) {
            if (_reflections[_excluded[i]] > rSupply || _balances[_excluded[i]] > tSupply) {
                return (_REFLECTION_TOTAL, _totalSupply);
            }
            rSupply = rSupply.sub(_reflections[_excluded[i]]);
            tSupply = tSupply.sub(_balances[_excluded[i]]);
        }
        if (rSupply < _REFLECTION_TOTAL.div(_totalSupply)) {
            return (_REFLECTION_TOTAL, _totalSupply);
        }
        return (rSupply, tSupply);
    } 

    function balanceOf(address account) public view override returns (uint256) {
        require(account != address(0), "Zero address not allowed");
        return tokenFromReflection(_reflections[account]);
    } 

    function _getDynamicLiquidityFee() private view returns (uint256) {
        uint256 balance = balanceOf(uniswapV2Pair);
        uint256 targetBalance = _totalSupply.mul(_targetLiquidity).div(_targetLiquidityDenominator);
        if (balance >= targetBalance) {
            return _minLiquidityFee;
        }
        uint256 feeRange = _maxLiquidityFee.sub(_minLiquidityFee);
        uint256 balanceRange = targetBalance.sub(balance);
        return _minLiquidityFee.add(balanceRange.mul(feeRange).div(targetBalance));
    } 

    function _takeLiquidity(uint256 tAmount, uint256 currentRate) private {
        uint256 tFee = tAmount.mul(_liquidityFee).div(100);
        uint256 rFee = tFee.mul(currentRate);
        _reflections[address(this)] = _reflections[address(this)].add(rFee);
        if (_isExcluded[address(this)]) {
            _balances[address(this)] = _balances[address(this)].add(tFee);
        }
        emit Transfer(msg.sender, address(this), tFee);
    } 

    function _transfer(address sender, address recipient, uint256 amount) private {
        require(sender != address(0), "Zero address not allowed");
        require(recipient != address(0), "Zero address not allowed");
        require(amount > 0, "Amount must be greater than zero");
        if (sender != owner() && recipient != owner()) {
            require(amount <= _maxTxAmount, "Amount exceeds max transaction limit");
            require(balanceOf(recipient).add(amount) <= _maxWalletAmount, "Wallet balance exceeds max limit");
        } 

        uint256 contractTokenBalance = balanceOf(address(this));
        bool overMinimumTokenBalance = contractTokenBalance >= _numTokensSellToAddToLiquidity;
        if (
            overMinimumTokenBalance &&
            !inSwapAndLiquify &&
            sender != uniswapV2Pair &&
            _swapAndLiquifyEnabled
        ) {
            swapAndLiquify(contractTokenBalance);
        } 

        bool takeFee = true; 

        if (_isEx            takeFee = false;
        } 

        _tokenTransfer(sender, recipient, amount, takeFee);
    } 

    function _tokenTransfer(address sender, address recipient, uint256 tAmount, bool takeFee) private {
        uint256 currentRate = _getRate();
        uint256 rAmount = tAmount.mul(currentRate);
        if (!takeFee) {
            _removeAllFee();
        } 

        (uint256 rTransferAmount, uint256 rFee) = _getValues(rAmount);
        uint256 tTransferAmount = tokenFromReflection(rTransferAmount);
        uint256 tFee = tAmount.sub(tTransferAmount); 

        _reflections[sender] = _reflections[sender].sub(rAmount);
        _reflections[recipient] = _reflections[recipient].add(rTransferAmount);
        _takeLiquidity(tFee, currentRate);
        _reflectFee(rFee, tFee);
        emit Transfer(sender, recipient, tTransferAmount); 

        if (!takeFee) {
            _restoreAllFee();
        }
    } 

    function _reflectFee(uint256 rFee, uint256 tFee) private {
        _reflections[address(this)] = _reflections[address(this)].add(rFee);
        if (_isExcluded[address(this)]) {
            _balances[address(this)] = _balances[address(this)].add(tFee);
        }
        emit Transfer(msg.sender, address(this), tFee);
    } 

    function _removeAllFee() private {
        if (_liquidityFee == 0) return; 

        _previousLiquidityFee = _liquidityFee;
        _liquidityFee = 0;
    } 

    function _restoreAllFee() private {
        _liquidityFee = _previousLiquidityFee;
    } 

    function swapAndLiquify(uint256 contractTokenBalance) private lockTheSwap {
        uint256 liquidityFee = _getDynamicLiquidityFee();
        uint256 tokensToSwap = contractTokenBalance.mul(liquidityFee).div(100);
        uint256 tokensToAdd = contractTokenBalance.sub(tokensToSwap); 

        // split the balance into halves
        uint256 half = tokensToSwap.div(2);
        uint256 otherHalf = tokensToSwap.sub(half); 

        uint256 initialBalance = address(this).balance; 

        // swap tokens for ETH
        swapTokensForEth(half); 

        // how much ETH did we just swap into?
        uint256 newBalance = address(this).balance.sub(initialBalance); 

        // add liquidity to uniswap
        addLiquidity(otherHalf, newBalance); 

        emit SwapAndLiquify(half, newBalance, otherHalf);
    } 

    function swapTokensForEth(uint256 tokenAmount) private {
        // generate the uniswap pair path of token -> weth
        address[] memory path = new address[](2);
        path[0] = address(this);
        path[1] = uniswapV2Router.WETH(); 

        _approve(address(this), address(uniswapV2Router), tokenAmount); 

        // make the swap
        uniswapV2Router.swapExactTokensForETHSupportingFeeOnTransferTokens(
            tokenAmount,
            0, // accept any amount of ETH
            path,
            address(this),
            block.timestamp.add(300)
        );
    } 

    function addLiquidity(uint256 tokenAmount, uint256 ethAmount) private {
        // approve token transfer to cover all possible scenarios
        _approve(address(this), address(uniswapV2Router), tokenAmount); 

        // add the liquidity
        uniswapV2Router.addLiquidityETH{value: ethAmount}(            address(this),
            tokenAmount,
            0, // slippage is unavoidable
            0, // slippage is unavoidable
            owner(),
            block.timestamp.add(300)
        );
    } 

    receive() external payable {} 

    function _buyBackTokens(uint256 amount) private {
        if (amount > 0) {
            // generate the uniswap pair path of token -> weth
            address[] memory path = new address[](2);
            path[0] = address(this);
            path[1] = uniswapV2Router.WETH(); 

            _approve(address(this), address(uniswapV2Router), amount); 

            // make the swap
            uniswapV2Router.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount,
                0, // accept any amount of ETH
                path,
                _deadAddress, // Burn tokens by sending them to the dead address
                block.timestamp.add(300)
            ); 

            emit BuyBackAndBurn(amount);
        }
    } 

    event BuyBackAndBurn(uint256 amount);
}
